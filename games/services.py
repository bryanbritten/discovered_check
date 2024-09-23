import json
import os
import requests
from datetime import datetime, timezone
from typing import Dict, List, Tuple, TypeAlias, Union

from django.db import transaction
from games.models import Game, Move, Opening

BaseTypes: TypeAlias = Union[str, int, bool, float]
PlayerData: TypeAlias = Dict[str, Union[BaseTypes, Dict[str, str]]]
ClockData: TypeAlias = Dict[str, int]
GameData: TypeAlias = Dict[str, Union[BaseTypes, List[int], PlayerData, ClockData]]


def _generate_game_object_from_raw_data(game: GameData) -> Game:
    eco = game.get('opening', {}).get('eco')
    opening = Opening.objects.filter(eco=eco).first()

    white_rating_start = game.get('players', {}).get('white', {}).get('rating')
    white_rating_gained = game.get('players', {}).get('white', {}).get('ratingDiff')
    white_rating_end = white_rating_start + white_rating_gained
    black_rating_start = game.get('players', {}).get('black', {}).get('rating')
    black_rating_gained = game.get('players', {}).get('black', {}).get('ratingDiff')
    black_rating_end = black_rating_start + black_rating_gained

    return Game(
        id=game.get('fullId'),
        game_id=game.get('id'),
        rated=game.get('rated'),
        variant=game.get('variant'),
        speed=game.get('speed'),
        perf=game.get('perf'),
        status=game.get('status'),
        white_player=game.get('players', {}).get('white', {}).get('user', {}).get('id'),
        white_rating_start=white_rating_start,
        white_rating_end=white_rating_end,
        black_player=game.get('players', {}).get('black', {}).get('user', {}).get('id'),
        black_rating_start=black_rating_start,
        black_rating_end=black_rating_end,
        winner=game.get('winner'),
        opening=opening,
        created_at=datetime.fromtimestamp(game.get('createdAt') / 1000, tz=timezone.utc),
        last_move_at=datetime.fromtimestamp(game.get('lastMoveAt') / 1000, tz=timezone.utc),
        initial_clock=game.get('clock', {}).get('initial'),
        increment=game.get('clock', {}).get('increment'),
        total_time=game.get('clock', {}).get('totalTime'),
    )


def _generate_clock_start_stop_times(clocks: List[int]) -> List[Tuple[int, int, int]]:
    if not clocks:
        return None

    # Lichess stores clock times in centiseconds
    clocks = [clock / 100 for clock in clocks]

    # Lichess also gives each player some amount of free time to make their first move
    # This means each player's clock on the second move is actually the initial clock
    white_clocks = clocks[::2]
    white_first_move_start_stop = [(white_clocks[0], white_clocks[0], 0)]
    white_subsequent_moves_start_stop = [
        (white_clocks[i-1], white_clocks[i], 0)
        for i in range(1, len(white_clocks))
    ]
    white_start_stop_times = white_first_move_start_stop + white_subsequent_moves_start_stop


    black_clocks = clocks[1::2]
    black_first_move_start_stop = [(black_clocks[0], black_clocks[0], 0)]
    black_subsequent_moves_start_stop = [
        (black_clocks[i-1], black_clocks[i], 0)
        for i in range(1, len(black_clocks))
    ]
    black_start_stop_times = black_first_move_start_stop + black_subsequent_moves_start_stop

    return {
        "white_start_stop_times": white_start_stop_times,
        "black_start_stop_times": black_start_stop_times,
    }


def _generate_move_objects_from_raw_data(game: Game, moves: str, clocks: List[int]) -> List[Move]:
    all_moves = []
    move_list = moves.split()
    start_stop_times = _generate_clock_start_stop_times(clocks)
    
    white_moves = move_list[::2]
    white_start_stop_times = start_stop_times.get('white_start_stop_times')
    for i, move in enumerate(white_moves):
        if clocks:
            start, stop, time_spent = white_start_stop_times[i]
        else:
            start = stop = time_spent = None
        
        move_obj = Move(
            game = game,
            move_number = i + 1,
            move = move,
            color = 'white',
            clock_start = start,
            clock_end = stop,
            time_spent = time_spent
        )
        all_moves.append(move_obj)
    
    black_moves = move_list[1::2]
    black_start_stop_times = start_stop_times.get('black_start_stop_times')
    for i, move in enumerate(black_moves):
        if clocks:
            start, stop, time_spent = black_start_stop_times[i]
        else:
            start = stop = time_spent = None
        
        move_obj = Move(
            game = game,
            move_number = i + 1,
            move = move,
            color = 'black',
            clock_start = start,
            clock_end = stop,
            time_spent = time_spent
        )
        all_moves.append(move_obj)
    
    return all_moves


def save_games_to_db(games: list[GameData]) -> None:
    all_games = []
    all_moves = []

    for game in games:
        cur_game = _generate_game_object_from_raw_data(game)
        all_games.append(cur_game)
    
        moves = _generate_move_objects_from_raw_data(cur_game, game.get('moves'), game.get('clocks', []))
        all_moves.extend(moves)
    
    with transaction.atomic():
        Game.objects.bulk_create(all_games)
        Move.objects.bulk_create(all_moves)


def fetch_games_from_api_service(username: str, token: str) -> None:
    url = f'https://lichess.org/api/games/user/{username}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/x-ndjson',
    }
    params = {
        'clocks': True,
        'opening': True,
        'literate': True,
        'accuracy': True,
        'evals': True,
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    content = response.text
    raw_game_data = content.strip().splitlines()
    games = [json.loads(game) for game in raw_game_data]

    save_games_to_db(games)


def fetch_games_from_db_service(username: str) -> list[GameData]:
    games = Game.objects.filter(white_player=username) | Game.objects.filter(black_player=username)
    return games


    