import requests
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import LichessToken, User
from .serializers import UserSerializer

LICHESS_TOKEN_URL = "https://lichess.org/api/token"
LICHESS_ACCOUNT_URL = "https://lichess.org/api/account"


@api_view(["POST"])
@permission_classes([AllowAny])
def lichess_oauth_exchange(request):
    """
    Exchange a Lichess OAuth authorization code (with PKCE code_verifier) for JWT tokens.

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

    # Exchange authorization code for access token
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

    # Fetch user profile from Lichess
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

    # Create or update the local user
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

    # Persist Lichess token
    LichessToken.objects.update_or_create(
        user=user,
        defaults={
            "access_token": access_token,
            "token_type": token_data.get("token_type", "Bearer"),
            "scope": token_data.get("scope", ""),
        },
    )

    # Issue JWT tokens
    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def token_refresh(request):
    """Thin wrapper — clients can also hit /api/auth/token/refresh/ directly."""
    from rest_framework_simplejwt.views import TokenRefreshView

    view = TokenRefreshView.as_view()
    return view(request._request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Return the current authenticated user's profile."""
    return Response(UserSerializer(request.user).data)
