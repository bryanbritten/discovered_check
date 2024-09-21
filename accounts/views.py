import requests
from accounts.services import (
    create_verifier, create_challenge, get_lichess_token, get_lichess_user_email
)
from django.shortcuts import redirect, render


def login(request):
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

def callback(request):
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
    print(f'User email: {email}')
    return redirect('dashboards:overview')

def logout(request):
    print('logging out the user')
    return redirect('accounts:login')

def signup(request):
    return render(request, 'accounts/signup.html')

def profile(request):
    return render(request, 'accounts/profile.html')