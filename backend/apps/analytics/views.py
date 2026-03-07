from django.db.models import Avg, Count, F, FloatField, Q, Sum
from django.db.models.functions import TruncMonth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics

from apps.games.models import Game, Move
from .models import TacticsOpportunity
from .serializers import TacticsOpportunitySerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def overview(request):
    """
    Overall statistics for the authenticated user.

    Query params:
        time_control_category: filter by tc category
        source: lichess | pgn_import
    """
    user = request.user
    qs = Game.objects.filter(user=user)

    tc = request.query_params.get("time_control_category")
    if tc:
        qs = qs.filter(time_control_category=tc)

    source = request.query_params.get("source")
    if source in ("lichess", "pgn_import"):
        qs = qs.filter(source=source)

    total = qs.count()
    if total == 0:
        return Response(_empty_overview())

    # Win/loss/draw overall
    result_counts = qs.values("user_result").annotate(count=Count("id"))
    result_map = {r["user_result"]: r["count"] for r in result_counts}

    wins = result_map.get("win", 0)
    losses = result_map.get("loss", 0)
    draws = result_map.get("draw", 0)

    # By color
    white_games = qs.filter(user_color="white")
    black_games = qs.filter(user_color="black")

    white_total = white_games.count()
    black_total = black_games.count()

    def color_stats(color_qs):
        counts = color_qs.values("user_result").annotate(count=Count("id"))
        m = {r["user_result"]: r["count"] for r in counts}
        tot = color_qs.count()
        return {
            "total": tot,
            "wins": m.get("win", 0),
            "losses": m.get("loss", 0),
            "draws": m.get("draw", 0),
            "win_rate": round(m.get("win", 0) / tot * 100, 1) if tot else 0,
        }

    # By time control category
    tc_counts = (
        qs.values("time_control_category")
        .annotate(
            total=Count("id"),
            wins=Count("id", filter=Q(user_result="win")),
            losses=Count("id", filter=Q(user_result="loss")),
            draws=Count("id", filter=Q(user_result="draw")),
        )
        .order_by("-total")
    )

    tc_breakdown = [
        {
            "category": r["time_control_category"],
            "total": r["total"],
            "wins": r["wins"],
            "losses": r["losses"],
            "draws": r["draws"],
            "win_rate": round(r["wins"] / r["total"] * 100, 1) if r["total"] else 0,
        }
        for r in tc_counts
    ]

    # By termination type
    termination_counts = (
        qs.values("termination")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Monthly trend (last 12 months)
    monthly = (
        qs.annotate(month=TruncMonth("played_at"))
        .values("month")
        .annotate(
            total=Count("id"),
            wins=Count("id", filter=Q(user_result="win")),
        )
        .order_by("month")
    )

    # Opening performance (top 10 by games played)
    openings = (
        qs.exclude(opening_name="")
        .values("opening_name", "opening_eco")
        .annotate(
            total=Count("id"),
            wins=Count("id", filter=Q(user_result="win")),
            losses=Count("id", filter=Q(user_result="loss")),
            draws=Count("id", filter=Q(user_result="draw")),
        )
        .order_by("-total")[:10]
    )

    return Response(
        {
            "total_games": total,
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "win_rate": round(wins / total * 100, 1) if total else 0,
            "as_white": color_stats(white_games),
            "as_black": color_stats(black_games),
            "by_time_control": tc_breakdown,
            "by_termination": [
                {"termination": r["termination"], "count": r["count"]}
                for r in termination_counts
            ],
            "monthly_trend": [
                {
                    "month": r["month"].strftime("%Y-%m"),
                    "total": r["total"],
                    "wins": r["wins"],
                    "win_rate": round(r["wins"] / r["total"] * 100, 1) if r["total"] else 0,
                }
                for r in monthly
            ],
            "top_openings": list(openings),
        }
    )


def _empty_overview():
    return {
        "total_games": 0,
        "wins": 0,
        "losses": 0,
        "draws": 0,
        "win_rate": 0,
        "as_white": {"total": 0, "wins": 0, "losses": 0, "draws": 0, "win_rate": 0},
        "as_black": {"total": 0, "wins": 0, "losses": 0, "draws": 0, "win_rate": 0},
        "by_time_control": [],
        "by_termination": [],
        "monthly_trend": [],
        "top_openings": [],
    }


class TacticsListView(generics.ListAPIView):
    """
    List tactics opportunities for the authenticated user's games.

    Query params:
        tactic_type: fork | pin | skewer
        missed: true | false
        time_control_category: filter by tc category
    """

    serializer_class = TacticsOpportunitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = TacticsOpportunity.objects.filter(game__user=self.request.user).select_related(
            "game", "move"
        )

        tactic_type = self.request.query_params.get("tactic_type")
        if tactic_type in ("fork", "pin", "skewer"):
            qs = qs.filter(tactic_type=tactic_type)

        missed = self.request.query_params.get("missed")
        if missed == "true":
            qs = qs.filter(missed=True)
        elif missed == "false":
            qs = qs.filter(missed=False)

        tc = self.request.query_params.get("time_control_category")
        if tc:
            qs = qs.filter(game__time_control_category=tc)

        return qs.order_by("-game__played_at")

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Append summary counts
        base_qs = TacticsOpportunity.objects.filter(game__user=request.user)
        summary = base_qs.aggregate(
            total=Count("id"),
            missed_total=Count("id", filter=Q(missed=True)),
            forks=Count("id", filter=Q(tactic_type="fork")),
            pins=Count("id", filter=Q(tactic_type="pin")),
            skewers=Count("id", filter=Q(tactic_type="skewer")),
            forks_missed=Count("id", filter=Q(tactic_type="fork", missed=True)),
            pins_missed=Count("id", filter=Q(tactic_type="pin", missed=True)),
            skewers_missed=Count("id", filter=Q(tactic_type="skewer", missed=True)),
        )

        response.data["summary"] = summary
        return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def time_analysis(request):
    """
    Time analysis for the authenticated user.

    Returns:
    - Average time per move overall and by time control
    - Distribution of moves by time category
    - Whether longer thinks correlate with different outcomes
      (tracked simply: moves after long thinks — did the game result improve?)
    """
    user = request.user

    games = Game.objects.filter(user=user, analysis_complete=True)

    tc = request.query_params.get("time_control_category")
    if tc:
        games = games.filter(time_control_category=tc)

    game_ids = games.values_list("id", flat=True)

    # User's moves only
    user_moves = Move.objects.filter(
        game_id__in=game_ids,
        time_spent__isnull=False,
    ).filter(
        # Only include moves where the user was playing
        Q(game__user_color="white", color="white") | Q(game__user_color="black", color="black")
    )

    # Overall time stats
    agg = user_moves.aggregate(
        avg_time=Avg("time_spent"),
        total_moves=Count("id"),
    )

    # Time by time control category
    by_tc = (
        user_moves.values("game__time_control_category")
        .annotate(avg_time=Avg("time_spent"), move_count=Count("id"))
        .order_by("game__time_control_category")
    )

    # Distribution by time category (from MoveTimeCategory)
    from .models import MoveTimeCategory

    category_dist = (
        MoveTimeCategory.objects.filter(move__game_id__in=game_ids)
        .filter(
            Q(move__game__user_color="white", move__color="white")
            | Q(move__game__user_color="black", move__color="black")
        )
        .values("time_category")
        .annotate(count=Count("id"))
        .order_by("time_category")
    )

    # Long-think analysis: after a long think (>30s), what happened to the game result?
    # We look at games where the user had at least one "long think" or "considered" move
    # and compare win rates to games where they didn't.
    games_with_long_think = set(
        MoveTimeCategory.objects.filter(
            move__game_id__in=game_ids,
            time_category__in=("long_think", "considered"),
        )
        .filter(
            Q(move__game__user_color="white", move__color="white")
            | Q(move__game__user_color="black", move__color="black")
        )
        .values_list("move__game_id", flat=True)
        .distinct()
    )

    games_with_long_think_qs = games.filter(id__in=games_with_long_think)
    games_without_long_think_qs = games.exclude(id__in=games_with_long_think)

    def win_rate_summary(qs):
        total = qs.count()
        wins = qs.filter(user_result="win").count()
        return {
            "total": total,
            "wins": wins,
            "win_rate": round(wins / total * 100, 1) if total else 0,
        }

    # Per-move time-category correlation with move quality is hard without an engine.
    # Instead we provide: average time spent broken down by whether the game was won/lost/drawn.
    time_by_result = (
        user_moves.values("game__user_result")
        .annotate(avg_time=Avg("time_spent"), move_count=Count("id"))
        .order_by("game__user_result")
    )

    return Response(
        {
            "overall": {
                "avg_time_per_move": round(agg["avg_time"], 2) if agg["avg_time"] else None,
                "total_moves_analyzed": agg["total_moves"],
            },
            "by_time_control": [
                {
                    "category": r["game__time_control_category"],
                    "avg_time_per_move": round(r["avg_time"], 2) if r["avg_time"] else None,
                    "move_count": r["move_count"],
                }
                for r in by_tc
            ],
            "time_category_distribution": [
                {"category": r["time_category"], "count": r["count"]}
                for r in category_dist
            ],
            "long_think_correlation": {
                "games_with_long_think": win_rate_summary(games_with_long_think_qs),
                "games_without_long_think": win_rate_summary(games_without_long_think_qs),
            },
            "time_by_result": [
                {
                    "result": r["game__user_result"],
                    "avg_time_per_move": round(r["avg_time"], 2) if r["avg_time"] else None,
                    "move_count": r["move_count"],
                }
                for r in time_by_result
            ],
        }
    )
