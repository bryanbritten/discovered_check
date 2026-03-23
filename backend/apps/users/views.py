import logging

import requests
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import LichessToken, User, UserSession
from .serializers import UserSerializer

logger = logging.getLogger(__name__)

LICHESS_TOKEN_URL = "https://lichess.org/api/token"
LICHESS_ACCOUNT_URL = "https://lichess.org/api/account"


def _issue_jwt_response(user: User, set_session_cookie: bool = False) -> Response:
    """Build a Response containing fresh JWT tokens (and optionally a session cookie)."""
    refresh = RefreshToken.for_user(user)
    response = Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        }
    )

    if set_session_cookie:
        session = UserSession.create_for_user(user)
        response.set_cookie(
            settings.PERSISTENT_SESSION_COOKIE_NAME,
            session.token,
            max_age=int(UserSession.LIFETIME.total_seconds()),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
        )

    return response


@api_view(["POST"])
@permission_classes([AllowAny])
def lichess_oauth_exchange(request):
    """
    Exchange a Lichess OAuth authorization code (with PKCE code_verifier) for JWT tokens.
    Also creates a persistent session cookie so subsequent logins skip OAuth entirely.

    Expected body:
        code: str
        code_verifier: str
        redirect_uri: str
    """
    code = request.data.get("code")
    code_verifier = request.data.get("code_verifier")
    redirect_uri = request.data.get("redirect_uri")

    if not all([code, code_verifier, redirect_uri]):
        return Response(
            {"error": "code, code_verifier, and redirect_uri are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if redirect_uri != settings.OAUTH_REDIRECT_URI:
        return Response(
            {"error": "Invalid redirect_uri."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not (43 <= len(code_verifier) <= 128):
        return Response(
            {"error": "code_verifier must be between 43 and 128 characters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(code) > 512:
        return Response(
            {"error": "Invalid authorization code."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(redirect_uri) > 2048:
        return Response(
            {"error": "Invalid redirect_uri."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token_resp = requests.post(
        LICHESS_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": redirect_uri,
            "client_id": settings.LICHESS_CLIENT_ID,
        },
        timeout=10,
    )

    if not token_resp.ok:
        logger.warning(
            "Lichess token exchange failed (status=%s): %s",
            token_resp.status_code,
            token_resp.text,
        )
        return Response(
            {"error": "Failed to exchange token with Lichess.", "detail": token_resp.text},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token_data = token_resp.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return Response(
            {"error": "No access token in Lichess response."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    account_resp = requests.get(
        LICHESS_ACCOUNT_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )

    if not account_resp.ok:
        return Response(
            {"error": "Failed to fetch Lichess account info."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    lichess_user = account_resp.json()
    lichess_id = lichess_user["id"]
    lichess_username = lichess_user["username"]

    user, _ = User.objects.get_or_create(
        lichess_id=lichess_id,
        defaults={
            "username": lichess_username,
            "lichess_username": lichess_username,
        },
    )

    if user.lichess_username != lichess_username:
        user.lichess_username = lichess_username
        user.save(update_fields=["lichess_username"])

    LichessToken.objects.update_or_create(
        user=user,
        defaults={
            "access_token": access_token,
            "token_type": token_data.get("token_type", "Bearer"),
            "scope": token_data.get("scope", ""),
        },
    )

    return _issue_jwt_response(user, set_session_cookie=True)


@api_view(["POST"])
@permission_classes([AllowAny])
def session_resume(request):
    """
    Issue fresh JWTs using the persistent session cookie, without requiring the
    user to re-authorize with Lichess.

    Returns 401 if the cookie is absent, invalid, or expired.
    """
    token = request.COOKIES.get(settings.PERSISTENT_SESSION_COOKIE_NAME)
    if not token:
        return Response({"error": "No session cookie."}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        session = UserSession.objects.select_related("user__lichess_token").get(token=token)
    except UserSession.DoesNotExist:
        return Response({"error": "Invalid session."}, status=status.HTTP_401_UNAUTHORIZED)

    if not session.is_valid():
        session.delete()
        return Response({"error": "Session expired."}, status=status.HTTP_401_UNAUTHORIZED)

    # Respect Lichess token expiry if it was populated
    try:
        lt = session.user.lichess_token
        if lt.expires_at and timezone.now() > lt.expires_at:
            session.delete()
            return Response(
                {"error": "Lichess token expired. Please re-authorize."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    except LichessToken.DoesNotExist:
        return Response({"error": "No Lichess token on record."}, status=status.HTTP_401_UNAUTHORIZED)

    session.touch()
    return _issue_jwt_response(session.user)


@api_view(["POST"])
@permission_classes([AllowAny])
def logout(request):
    """
    Invalidate the persistent session cookie (full logout).
    The frontend is responsible for clearing JWTs from localStorage.
    """
    token = request.COOKIES.get(settings.PERSISTENT_SESSION_COOKIE_NAME)
    if token:
        UserSession.objects.filter(token=token).delete()

    response = Response({"detail": "Logged out."})
    response.delete_cookie(settings.PERSISTENT_SESSION_COOKIE_NAME)
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Return the current authenticated user's profile."""
    return Response(UserSerializer(request.user).data)
