import base64
import hashlib
import os
import requests
import secrets
from dotenv import load_dotenv

from accounts.models import AuthToken, CustomUser

load_dotenv()

def create_verifier():
    return secrets.token_urlsafe(64)

def create_challenge(verifier):
    verifier_bytes = verifier.encode('utf-8')
    verifier_hash = hashlib.sha256(verifier_bytes).digest()
    verifier_hash_b64 = base64.urlsafe_b64encode(verifier_hash).rstrip(b'=').decode('utf-8')
    return verifier_hash_b64

def get_lichess_token(auth_code, verifier, callback_url):
    token_url = 'https://lichess.org/api/token'
    data = {
        'grant_type': 'authorization_code',
        'redirect_uri': callback_url,
        'client_id': os.getenv('LICHESS_CLIENT_ID'),
        'code': auth_code,
        'code_verifier': verifier,
    }
    response = requests.post(token_url, json=data)
    return response.json()

def get_lichess_user_email(access_token):
    user_url = 'https://lichess.org/api/account/email'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(user_url, headers=headers)
    return response.json()

def revoke_token(user: CustomUser) -> None:
    token = AuthToken.objects.get(user=user)
    access_token = token.access_token

    # revoke it on Lichess's side
    url = 'https://lichess.org/api/token'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.delete(url, headers=headers)
    if response.status_code != 204:
        raise Exception('Failed to revoke token')

    # revoke it on Discovered Check's side
    token.access_token = None
    token.token_acquired_at = None
    token.token_expires_at = None
    token.save()
