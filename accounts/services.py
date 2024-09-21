import secrets
import hashlib
import base64
import requests


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
        'client_id': 'discoveredcheck.io',
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