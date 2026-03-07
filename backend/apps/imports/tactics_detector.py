"""
Human-centered tactics detector (no engine required).

Detects forks, pins, and skewers purely from board geometry.
"""

from __future__ import annotations

import chess


PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 100,
}


def _piece_value(piece_type: int) -> int:
    return PIECE_VALUES.get(piece_type, 0)


def detect_fork(board: chess.Board, color: chess.Color) -> list[dict]:
    """
    Detect forks: a piece attacks two or more of the opponent's pieces simultaneously.
    Only flags as a fork if the attacker is less valuable than at least two targets.
    """
    forks = []
    opponent = not color

    for square, piece in board.piece_map().items():
        if piece.color != color:
            continue

        attacked_squares = list(board.attacks(square))
        valuable_targets = [
            sq
            for sq in attacked_squares
            if board.piece_at(sq) is not None
            and board.piece_at(sq).color == opponent
            and _piece_value(board.piece_at(sq).piece_type) >= _piece_value(piece.piece_type)
        ]

        if len(valuable_targets) >= 2:
            forks.append(
                {
                    "attacking_square": chess.square_name(square),
                    "attacking_piece": piece.symbol().upper(),
                    "targets": [
                        {
                            "square": chess.square_name(sq),
                            "piece": board.piece_at(sq).symbol().upper(),
                        }
                        for sq in valuable_targets
                    ],
                }
            )

    return forks


def detect_pin(board: chess.Board, color: chess.Color) -> list[dict]:
    """
    Detect pins: a sliding piece attacks a less valuable piece that shields
    a more valuable piece (or king) behind it.
    """
    pins = []
    opponent = not color

    sliding_pieces = {chess.BISHOP, chess.ROOK, chess.QUEEN}

    for square, piece in board.piece_map().items():
        if piece.color != color or piece.piece_type not in sliding_pieces:
            continue

        # Get the ray directions this piece can slide
        rays = _get_rays(piece.piece_type)

        for direction in rays:
            sq = square
            found_pieces = []
            while True:
                sq = _next_square(sq, direction)
                if sq is None:
                    break
                target = board.piece_at(sq)
                if target is None:
                    continue
                found_pieces.append((sq, target))
                if len(found_pieces) == 2:
                    break

            if len(found_pieces) < 2:
                continue

            pinned_sq, pinned_piece = found_pieces[0]
            shielded_sq, shielded_piece = found_pieces[1]

            # The pinned piece must be opponent's, shielded must also be opponent's and more valuable
            if (
                pinned_piece.color == opponent
                and shielded_piece.color == opponent
                and _piece_value(shielded_piece.piece_type) > _piece_value(pinned_piece.piece_type)
            ):
                pins.append(
                    {
                        "attacking_square": chess.square_name(square),
                        "attacking_piece": piece.symbol().upper(),
                        "targets": [
                            {
                                "square": chess.square_name(pinned_sq),
                                "piece": pinned_piece.symbol().upper(),
                                "role": "pinned",
                            },
                            {
                                "square": chess.square_name(shielded_sq),
                                "piece": shielded_piece.symbol().upper(),
                                "role": "shielded",
                            },
                        ],
                    }
                )

    return pins


def detect_skewer(board: chess.Board, color: chess.Color) -> list[dict]:
    """
    Detect skewers: a sliding piece attacks a more valuable piece that must move,
    exposing a less valuable piece behind it.
    """
    skewers = []
    opponent = not color
    sliding_pieces = {chess.BISHOP, chess.ROOK, chess.QUEEN}

    for square, piece in board.piece_map().items():
        if piece.color != color or piece.piece_type not in sliding_pieces:
            continue

        rays = _get_rays(piece.piece_type)

        for direction in rays:
            sq = square
            found_pieces = []
            while True:
                sq = _next_square(sq, direction)
                if sq is None:
                    break
                target = board.piece_at(sq)
                if target is None:
                    continue
                found_pieces.append((sq, target))
                if len(found_pieces) == 2:
                    break

            if len(found_pieces) < 2:
                continue

            front_sq, front_piece = found_pieces[0]
            back_sq, back_piece = found_pieces[1]

            if (
                front_piece.color == opponent
                and back_piece.color == opponent
                and _piece_value(front_piece.piece_type) > _piece_value(back_piece.piece_type)
            ):
                skewers.append(
                    {
                        "attacking_square": chess.square_name(square),
                        "attacking_piece": piece.symbol().upper(),
                        "targets": [
                            {
                                "square": chess.square_name(front_sq),
                                "piece": front_piece.symbol().upper(),
                                "role": "front",
                            },
                            {
                                "square": chess.square_name(back_sq),
                                "piece": back_piece.symbol().upper(),
                                "role": "back",
                            },
                        ],
                    }
                )

    return skewers


def analyze_game_tactics(game_obj) -> None:
    """
    Run all tactic detectors on every position in a game and
    save TacticsOpportunity records.

    Only looks for tactics available to the user's color that were NOT taken.
    """
    from apps.analytics.models import GameAnalysis, TacticsOpportunity
    from apps.games.models import Move

    user_color = chess.WHITE if game_obj.user_color == "white" else chess.BLACK
    moves = list(Move.objects.filter(game=game_obj).order_by("ply"))

    opportunities: list[TacticsOpportunity] = []

    for i, move_obj in enumerate(moves):
        # We detect tactics available BEFORE this move (in fen_before).
        # We only care about tactics available to the user.
        # The user's color corresponds to the side-to-move in the fen.
        board = chess.Board(move_obj.fen_before)
        if board.turn != user_color:
            continue

        # What tactics existed in this position?
        forks = detect_fork(board, user_color)
        pins = detect_pin(board, user_color)
        skewers = detect_skewer(board, user_color)

        played_uci = move_obj.uci

        def _best_tactical_move(detections: list[dict]) -> str | None:
            # Simple heuristic: prefer the move that captures the most valuable target.
            # For forks/pins/skewers the "attacking_square" already has the piece.
            if not detections:
                return None
            # Return the first detection's attacking square as the move origin.
            # We don't have a complete move here — for simplicity we flag the opportunity
            # without requiring the exact best move UCI.
            return detections[0]["attacking_square"]

        for fork in forks:
            opp = TacticsOpportunity(
                game=game_obj,
                move=move_obj,
                tactic_type="fork",
                missed=True,  # Will refine below
                best_move_uci=fork["attacking_square"],
                played_move_uci=played_uci,
                attacking_piece=fork["attacking_piece"],
                attacking_square=fork["attacking_square"],
                targets=fork["targets"],
                fen=move_obj.fen_before,
                description=_describe_fork(fork),
            )
            # The tactic is "not missed" if the played move uses the same attacker
            if played_uci[:2] == fork["attacking_square"]:
                opp.missed = False
            opportunities.append(opp)

        for pin in pins:
            opp = TacticsOpportunity(
                game=game_obj,
                move=move_obj,
                tactic_type="pin",
                missed=True,
                best_move_uci=pin["attacking_square"],
                played_move_uci=played_uci,
                attacking_piece=pin["attacking_piece"],
                attacking_square=pin["attacking_square"],
                targets=pin["targets"],
                fen=move_obj.fen_before,
                description=_describe_pin(pin),
            )
            if played_uci[:2] == pin["attacking_square"]:
                opp.missed = False
            opportunities.append(opp)

        for skewer in skewers:
            opp = TacticsOpportunity(
                game=game_obj,
                move=move_obj,
                tactic_type="skewer",
                missed=True,
                best_move_uci=skewer["attacking_square"],
                played_move_uci=played_uci,
                attacking_piece=skewer["attacking_piece"],
                attacking_square=skewer["attacking_square"],
                targets=skewer["targets"],
                fen=move_obj.fen_before,
                description=_describe_skewer(skewer),
            )
            if played_uci[:2] == skewer["attacking_square"]:
                opp.missed = False
            opportunities.append(opp)

    TacticsOpportunity.objects.bulk_create(opportunities)

    # Update GameAnalysis
    total = len(opportunities)
    missed = sum(1 for o in opportunities if o.missed)
    GameAnalysis.objects.filter(game=game_obj).update(
        tactics_opportunities_count=total,
        tactics_missed_count=missed,
    )


def _describe_fork(fork: dict) -> str:
    targets = ", ".join(f"{t['piece']} on {t['square']}" for t in fork["targets"])
    return f"{fork['attacking_piece']} on {fork['attacking_square']} forks {targets}"


def _describe_pin(pin: dict) -> str:
    pinned = next((t for t in pin["targets"] if t.get("role") == "pinned"), pin["targets"][0])
    shielded = next((t for t in pin["targets"] if t.get("role") == "shielded"), pin["targets"][-1])
    return (
        f"{pin['attacking_piece']} on {pin['attacking_square']} pins "
        f"{pinned['piece']} on {pinned['square']} against "
        f"{shielded['piece']} on {shielded['square']}"
    )


def _describe_skewer(skewer: dict) -> str:
    front = next((t for t in skewer["targets"] if t.get("role") == "front"), skewer["targets"][0])
    back = next((t for t in skewer["targets"] if t.get("role") == "back"), skewer["targets"][-1])
    return (
        f"{skewer['attacking_piece']} on {skewer['attacking_square']} skewers "
        f"{front['piece']} on {front['square']} to win "
        f"{back['piece']} on {back['square']}"
    )


# ─── Ray helpers ─────────────────────────────────────────────────────────────

ROOK_DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]
BISHOP_DIRECTIONS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
QUEEN_DIRECTIONS = ROOK_DIRECTIONS + BISHOP_DIRECTIONS


def _get_rays(piece_type: int) -> list[tuple[int, int]]:
    if piece_type == chess.ROOK:
        return ROOK_DIRECTIONS
    if piece_type == chess.BISHOP:
        return BISHOP_DIRECTIONS
    return QUEEN_DIRECTIONS


def _next_square(sq: int, direction: tuple[int, int]) -> int | None:
    file = chess.square_file(sq) + direction[0]
    rank = chess.square_rank(sq) + direction[1]
    if 0 <= file <= 7 and 0 <= rank <= 7:
        return chess.square(file, rank)
    return None
