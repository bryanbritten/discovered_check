import base64
import hashlib
import os
import requests
import secrets
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from accounts.models import AuthToken, CustomUser, Profile

load_dotenv()

def create_verifier():
    return secrets.token_urlsafe(64)

def create_challenge(verifier):
    verifier_bytes = verifier.encode('utf-8')
    verifier_hash = hashlib.sha256(verifier_bytes).digest()
    verifier_hash_b64 = base64.urlsafe_b64encode(verifier_hash).rstrip(b'=').decode('utf-8')
    return verifier_hash_b64

def create_or_update_user_profile(user: CustomUser, user_info: dict) -> None:
    profile, _ = Profile.objects.get_or_create(user=user, platform='lichess')
    profile.title = user_info.get('title')
    profile.blitz_games = user_info.get('perfs', {}).get('blitz', {}).get('games', 0)
    profile.blitz_rating = user_info.get('perfs', {}).get('blitz', {}).get('rating', 0)
    profile.bullet_games = user_info.get('perfs', {}).get('bullet', {}).get('games', 0)
    profile.bullet_rating = user_info.get('perfs', {}).get('bullet', {}).get('rating', 0)
    profile.ultra_bullet_games = user_info.get('perfs', {}).get('ultraBullet', {}).get('games', 0)
    profile.ultra_bullet_rating = user_info.get('perfs', {}).get('ultraBullet', {}).get('rating', 0)
    profile.rapid_games = user_info.get('perfs', {}).get('rapid', {}).get('games', 0)
    profile.rapid_rating = user_info.get('perfs', {}).get('rapid', {}).get('rating', 0)
    profile.puzzles_completed = user_info.get('perfs', {}).get('puzzle', {}).get('games', 0)
    profile.puzzles_rating = user_info.get('perfs', {}).get('puzzle', {}).get('rating', 0)
    profile.classical_games = user_info.get('perfs', {}).get('classical', {}).get('games', 0)
    profile.classical_rating = user_info.get('perfs', {}).get('classical', {}).get('rating', 0)
    profile.member_since = datetime.fromtimestamp(user_info.get('createdAt') / 1000, tz=timezone.utc)
    profile.last_seen = datetime.fromtimestamp(user_info.get('seenAt') / 1000, tz=timezone.utc)
    profile.is_disabled = user_info.get('disabled', False)
    profile.violated_tos = user_info.get('tosViolation', False)
    profile.save()


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

def get_lichess_user(access_token):
    user_url = 'https://lichess.org/api/account'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(user_url, headers=headers)
    return response.json()

def store_token(user: CustomUser, token_response: dict) -> None:
    token, _ = AuthToken.objects.get_or_create(user=user)
    token.access_token=token_response.get('access_token')
    token.token_acquired_at=token_response.get('token_acquired_at', datetime.now(tz=timezone.utc))
    token.token_expires_at=token_response.get(
            'token_expires_at', datetime.now(tz=timezone.utc) + timedelta(days=14)
        )
    token.save()

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
