"""
Parse PGN files and persist games + moves to the database.

This module is intentionally kept synchronous so it can be called
from a management command, a Celery task, or directly in a view.
"""

from __future__ import annotations

import io
import re
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import chess
import chess.pgn

if TYPE_CHECKING:
    from apps.imports.models import PGNImport
    from apps.users.models import User

TIME_CONTROL_CATEGORIES = {
    "ultrabullet": lambda t, i: t + i * 40 < 30,
    "bullet": lambda t, i: 30 <= t + i * 40 < 180,
    "blitz": lambda t, i: 180 <= t + i * 40 < 600,
    "rapid": lambda t, i: 600 <= t + i * 40 < 1800,
    "classical": lambda t, i: 1800 <= t + i * 40,
}

CLK_REGEX = re.compile(r"\[%clk (\d+):(\d+):(\d+(?:\.\d+)?)\]")
EVAL_REGEX = re.compile(r"\[%eval ([^\]]+)\]")


def categorize_time_control(initial: int, increment: int) -> str:
    for category, predicate in TIME_CONTROL_CATEGORIES.items():
        if predicate(initial, increment):
            return category
    return "unknown"


def parse_clock(comment: str) -> float | None:
    """Extract clock time in seconds from a PGN move comment."""
    m = CLK_REGEX.search(comment or "")
    if not m:
        return None
    h, mn, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mn * 60 + s


def parse_pgn_string(pgn_text: str, user: "User", pgn_import: "PGNImport | None" = None) -> tuple[int, int]:
    """
    Parse all games from a PGN string and save them to the database.

    Returns:
        (games_saved, games_failed)
    """
    from apps.analytics.models import GameAnalysis, MoveTimeCategory
    from apps.games.models import Game, Move

    games_saved = 0
    games_failed = 0

    pgn_io = io.StringIO(pgn_text)

    while True:
        try:
            game = chess.pgn.read_game(pgn_io)
        except Exception:
            games_failed += 1
            continue

        if game is None:
            break

        try:
            _save_game(game, user, pgn_import)
            games_saved += 1
        except Exception:
            games_failed += 1

    return games_saved, games_failed


def _save_game(
    pgn_game: chess.pgn.Game,
    user: "User",
    pgn_import: "PGNImport | None",
) -> None:
    from apps.analytics.models import GameAnalysis, MoveTimeCategory
    from apps.games.models import Game, Move

    headers = pgn_game.headers

    # Determine which color the user played
    white = headers.get("White", "").lower()
    black = headers.get("Black", "").lower()
    username_lower = (user.lichess_username or user.username or "").lower()

    if username_lower and white == username_lower:
        user_color = "white"
    elif username_lower and black == username_lower:
        user_color = "black"
    else:
        # Default to white if we can't determine
        user_color = "white"

    # Parse result
    result_str = headers.get("Result", "*")
    if result_str == "1-0":
        result = "white"
    elif result_str == "0-1":
        result = "black"
    elif result_str == "1/2-1/2":
        result = "draw"
    else:
        result = "draw"

    if result == "draw":
        user_result = "draw"
    elif (result == "white" and user_color == "white") or (result == "black" and user_color == "black"):
        user_result = "win"
    else:
        user_result = "loss"

    # Time control
    tc_str = headers.get("TimeControl", "-")
    initial_time = None
    increment = 0
    if "+" in tc_str:
        parts = tc_str.split("+")
        try:
            initial_time = int(parts[0])
            increment = int(parts[1])
        except (ValueError, IndexError):
            pass
    elif tc_str != "-":
        try:
            initial_time = int(tc_str)
        except ValueError:
            pass

    tc_category = (
        categorize_time_control(initial_time, increment) if initial_time is not None else "unknown"
    )

    # Termination
    termination_header = headers.get("Termination", "").lower()
    if "checkmate" in termination_header:
        termination = "checkmate"
    elif "resign" in termination_header or "abandoned" in termination_header:
        termination = "resignation"
    elif "time" in termination_header or "flag" in termination_header:
        termination = "timeout"
    elif "stalemate" in termination_header:
        termination = "stalemate"
    elif "repetition" in termination_header:
        termination = "repetition"
    elif "insufficient" in termination_header or "material" in termination_header:
        termination = "insufficient"
    elif result_str in ("1/2-1/2",):
        termination = "draw"
    else:
        termination = "other"

    # Played at
    date_str = headers.get("UTCDate", headers.get("Date", ""))
    time_str = headers.get("UTCTime", "00:00:00")
    try:
        played_at = datetime.strptime(f"{date_str} {time_str}", "%Y.%m.%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        played_at = datetime.now(tz=timezone.utc)

    # Ratings
    try:
        white_rating = int(headers.get("WhiteElo", ""))
    except ValueError:
        white_rating = None
    try:
        black_rating = int(headers.get("BlackElo", ""))
    except ValueError:
        black_rating = None

    user_rating = white_rating if user_color == "white" else black_rating
    opponent_rating = black_rating if user_color == "white" else white_rating

    lichess_game_id = headers.get("Site", "").split("/")[-1] or None
    source = "lichess" if lichess_game_id else "pgn_import"

    # Check for duplicate
    if lichess_game_id:
        if Game.objects.filter(user=user, lichess_game_id=lichess_game_id).exists():
            return  # Skip duplicate

    # Export raw PGN
    exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
    raw_pgn = pgn_game.accept(exporter)

    game_obj = Game.objects.create(
        user=user,
        source=source,
        lichess_game_id=lichess_game_id,
        pgn_import=pgn_import,
        white_username=headers.get("White", ""),
        black_username=headers.get("Black", ""),
        user_color=user_color,
        white_rating=white_rating,
        black_rating=black_rating,
        user_rating=user_rating,
        opponent_rating=opponent_rating,
        result=result,
        user_result=user_result,
        termination=termination,
        time_control=tc_str,
        time_control_category=tc_category,
        initial_time=initial_time,
        increment=increment,
        opening_name=headers.get("Opening", ""),
        opening_eco=headers.get("ECO", ""),
        pgn=raw_pgn,
        played_at=played_at,
        analysis_complete=False,
    )

    # Parse moves
    board = pgn_game.board()
    moves_to_create = []
    time_categories_to_create = []

    prev_white_clock = initial_time
    prev_black_clock = initial_time
    ply = 1

    node = pgn_game
    while node.variations:
        next_node = node.variations[0]
        move = next_node.move
        comment = next_node.comment or ""

        color = "white" if board.turn == chess.WHITE else "black"
        move_number = (ply + 1) // 2

        fen_before = board.fen()
        board.push(move)
        fen_after = board.fen()

        clock_remaining = parse_clock(comment)

        # Calculate time spent
        time_spent = None
        if clock_remaining is not None:
            if color == "white" and prev_white_clock is not None:
                time_spent = prev_white_clock - clock_remaining + increment
                prev_white_clock = clock_remaining
            elif color == "black" and prev_black_clock is not None:
                time_spent = prev_black_clock - clock_remaining + increment
                prev_black_clock = clock_remaining

        if time_spent is not None and time_spent < 0:
            time_spent = 0

        move_obj = Move(
            game=game_obj,
            ply=ply,
            move_number=move_number,
            color=color,
            san=next_node.san(),
            uci=move.uci(),
            fen_before=fen_before,
            fen_after=fen_after,
            clock_time_remaining=clock_remaining,
            time_spent=time_spent,
        )
        moves_to_create.append(move_obj)

        ply += 1
        node = next_node

    Move.objects.bulk_create(moves_to_create)

    # Classify moves by time spent & build MoveTimeCategory records
    saved_moves = Move.objects.filter(game=game_obj).order_by("ply")
    for move_obj in saved_moves:
        if move_obj.time_spent is None:
            continue
        t = move_obj.time_spent
        if t < 2:
            cat = "instant"
        elif t < 10:
            cat = "quick"
        elif t < 30:
            cat = "normal"
        elif t < 60:
            cat = "considered"
        else:
            cat = "long_think"
        time_categories_to_create.append(
            MoveTimeCategory(move=move_obj, time_category=cat)
        )

    MoveTimeCategory.objects.bulk_create(time_categories_to_create)

    # Compute per-game time stats
    user_moves = saved_moves.filter(color=user_color, time_spent__isnull=False)
    times = list(user_moves.values_list("time_spent", flat=True))
    if times:
        times_sorted = sorted(times)
        avg_time = sum(times) / len(times)
        mid = len(times_sorted) // 2
        median_time = (
            times_sorted[mid]
            if len(times_sorted) % 2
            else (times_sorted[mid - 1] + times_sorted[mid]) / 2
        )
        max_time = max(times)
        total_time = sum(times)
        time_pressure = sum(
            1
            for m in user_moves.filter(time_spent__isnull=False)
            if initial_time and m.clock_time_remaining is not None
            and m.clock_time_remaining < initial_time * 0.1
        )
    else:
        avg_time = median_time = max_time = total_time = None
        time_pressure = 0

    GameAnalysis.objects.create(
        game=game_obj,
        avg_time_per_move=avg_time,
        median_time_per_move=median_time,
        max_time_per_move=max_time,
        total_time_used=total_time,
        time_pressure_moves_count=time_pressure,
    )

    game_obj.analysis_complete = True
    game_obj.save(update_fields=["analysis_complete"])
