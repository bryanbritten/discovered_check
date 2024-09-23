import os
import requests
from dotenv import load_dotenv

from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser

from accounts.services import (
    create_challenge,
    create_verifier,
    create_or_update_user_profile,
    get_lichess_token,
    get_lichess_user,
    store_token,
    revoke_token,
)

load_dotenv()

def Login(request):
    if request.method == 'GET':
        return render(request, 'accounts/login.html')

    verifier = create_verifier()
    challenge = create_challenge(verifier)
    request.session['verifier'] = verifier
    params = {
        'client_id': os.getenv('LICHESS_CLIENT_ID'),
        'response_type': 'code',
        'scope': 'preference:read',
        'redirect_uri': request.build_absolute_uri('/accounts/callback/'),
        'code_challenge': challenge,
        'code_challenge_method': 'S256',
    }
    lichess_oauth_url = f'https://lichess.org/oauth?{requests.compat.urlencode(params)}'
    return redirect(lichess_oauth_url)


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
    
    user_info = get_lichess_user(access_token)
    username = user_info.get('id')
    if not username:
        return redirect(request, 'accounts/error.html', {'error': 'No username found in response'})
    
    user, created = CustomUser.objects.get_or_create(username=username)
    if created:
        user.set_unusable_password()
        user.save()
    
    store_token(user, token_response)
    create_or_update_user_profile(user, user_info)
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