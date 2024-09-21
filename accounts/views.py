from datetime import datetime, timedelta, timezone
import requests
from accounts.services import (
    create_verifier,
    create_challenge,
    get_lichess_token,
    get_lichess_user_email,
    revoke_token
)
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from accounts.models import AuthToken, CustomUser


def Login(request):
    if request.method == 'POST':
        verifier = create_verifier()
        challenge = create_challenge(verifier)
        request.session['verifier'] = verifier
        params = {
            'client_id': 'discoveredcheck.io',
            'response_type': 'code',
            'scope': 'email:read',
            'redirect_uri': request.build_absolute_uri('/accounts/callback/'),
            'code_challenge': challenge,
            'code_challenge_method': 'S256',
        }
        lichess_oauth_url = f'https://lichess.org/oauth?{requests.compat.urlencode(params)}'
        return redirect(lichess_oauth_url)

    return render(request, 'accounts/login.html')

def Callback(request):
    verifier = request.session['verifier']

    if not verifier:
        return redirect(request, 'accounts/error.html', {'error': 'No verifier found in session'})

    auth_code = request.GET['code']
    if not auth_code:
        return redirect(request, 'accounts/error.html', {'error': 'No auth code found in request'})
    
    callback_url = request.build_absolute_uri('/accounts/callback/')
    token_response = get_lichess_token(auth_code, verifier, callback_url)
    access_token = token_response.get('access_token')
    if not access_token:
        return redirect(request, 'accounts/error.html', {'error': 'No access token found in response'})
    
    user_info = get_lichess_user_email(access_token)
    email = user_info.get('email')
    if not email:
        return redirect(request, 'accounts/error.html', {'error': 'No email found in response'})
    
    user, created = CustomUser.objects.get_or_create(email=email)
    if created:
        user.set_unusable_password()
        user.save()
    
    token, _ = AuthToken.objects.get_or_create(user=user)
    token.access_token=access_token
    token.token_acquired_at=token_response.get('token_acquired_at', datetime.now(tz=timezone.utc))
    token.token_expires_at=token_response.get(
            'token_expires_at', datetime.now(tz=timezone.utc) + timedelta(days=14)
        )
    token.save()
    login(request, user)
    return redirect('dashboards:overview')

def Logout(request):
    revoke_token(request.user)
    logout(request)
    return redirect('accounts:login')

def Signup(request):
    return render(request, 'accounts/signup.html')

@login_required
def Profile(request):
    return render(request, 'accounts/profile.html')