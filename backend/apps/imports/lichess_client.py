"""
Lichess API client for fetching a user's games.
"""

from __future__ import annotations

import requests

LICHESS_GAMES_URL = "https://lichess.org/api/games/user/{username}"


def fetch_user_games(
    access_token: str,
    username: str,
    since: int | None = None,
    max_games: int = 200,
) -> str:
    """
    Fetch games from Lichess in PGN format.

    Args:
        access_token: Lichess OAuth access token
        username: Lichess username
        since: Unix timestamp in milliseconds — only fetch games after this time
        max_games: Maximum number of games to fetch per request

    Returns:
        Raw PGN string (may be empty)
    """
    params: dict = {
        "max": max_games,
        "clocks": "true",
        "opening": "true",
        "pgnInJson": "false",
        "literate": "false",
        "sort": "dateAsc",
    }

    if since is not None:
        params["since"] = since

    resp = requests.get(
        LICHESS_GAMES_URL.format(username=username),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/x-chess-pgn",
        },
        params=params,
        timeout=60,
        stream=True,
    )

    if not resp.ok:
        raise RuntimeError(f"Lichess API error {resp.status_code}: {resp.text[:200]}")

    return resp.text
