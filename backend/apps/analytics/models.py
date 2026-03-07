from django.db import models

from apps.games.models import Game, Move


class TacticsOpportunity(models.Model):
    """A position in a game where a tactic (fork, pin, or skewer) was available."""

    class TacticType(models.TextChoices):
        FORK = "fork", "Fork"
        PIN = "pin", "Pin"
        SKEWER = "skewer", "Skewer"

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="tactics_opportunities")
    move = models.ForeignKey(Move, on_delete=models.CASCADE, related_name="tactics_opportunities")

    tactic_type = models.CharField(max_length=10, choices=TacticType.choices)

    # Was the tactic missed by the user playing in this game?
    missed = models.BooleanField()

    # The tactic details
    best_move_uci = models.CharField(max_length=5)     # optimal tactical move
    played_move_uci = models.CharField(max_length=5, blank=True, default="")   # what was played

    # Piece doing the attacking
    attacking_piece = models.CharField(max_length=2)   # e.g., "N", "B", "Q"
    attacking_square = models.CharField(max_length=2)  # e.g., "f3"

    # Pieces/squares involved (JSON array of {"square": "e5", "piece": "R"})
    targets = models.JSONField(default=list)

    fen = models.TextField()  # position FEN where tactic is available
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["game", "move__ply"]

    def __str__(self):
        status = "missed" if self.missed else "found"
        return f"{self.tactic_type} in {self.game} move {self.move.ply} ({status})"


class MoveTimeCategory(models.Model):
    """Categorizes a move by how long the player spent thinking."""

    class TimeCategory(models.TextChoices):
        INSTANT = "instant", "Instant"           # < 2 seconds
        QUICK = "quick", "Quick"                  # 2–10 seconds
        NORMAL = "normal", "Normal"               # 10–30 seconds
        CONSIDERED = "considered", "Considered"   # 30–60 seconds
        LONG_THINK = "long_think", "Long Think"   # > 60 seconds

    move = models.OneToOneField(Move, on_delete=models.CASCADE, related_name="time_category")
    time_category = models.CharField(max_length=15, choices=TimeCategory.choices)

    def __str__(self):
        return f"{self.move} — {self.time_category}"


class GameAnalysis(models.Model):
    """Aggregated analysis results for a game."""

    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name="analysis")

    # Tactics summary
    tactics_opportunities_count = models.IntegerField(default=0)
    tactics_missed_count = models.IntegerField(default=0)

    # Time summary (user's moves only)
    avg_time_per_move = models.FloatField(null=True, blank=True)
    median_time_per_move = models.FloatField(null=True, blank=True)
    max_time_per_move = models.FloatField(null=True, blank=True)
    total_time_used = models.FloatField(null=True, blank=True)

    # Time pressure: moves made with < 10% of initial time remaining
    time_pressure_moves_count = models.IntegerField(default=0)

    analyzed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analysis for {self.game}"
