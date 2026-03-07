import uuid

from django.db import models

from apps.users.models import User


class Game(models.Model):
    class Source(models.TextChoices):
        LICHESS = "lichess", "Lichess"
        PGN_IMPORT = "pgn_import", "PGN Import"

    class Color(models.TextChoices):
        WHITE = "white", "White"
        BLACK = "black", "Black"

    class Result(models.TextChoices):
        WHITE = "white", "White wins"
        BLACK = "black", "Black wins"
        DRAW = "draw", "Draw"

    class UserResult(models.TextChoices):
        WIN = "win", "Win"
        LOSS = "loss", "Loss"
        DRAW = "draw", "Draw"

    class Termination(models.TextChoices):
        CHECKMATE = "checkmate", "Checkmate"
        RESIGNATION = "resignation", "Resignation"
        TIMEOUT = "timeout", "Timeout"
        DRAW = "draw", "Draw"
        STALEMATE = "stalemate", "Stalemate"
        REPETITION = "repetition", "Repetition"
        INSUFFICIENT = "insufficient", "Insufficient material"
        OTHER = "other", "Other"

    class TimeControlCategory(models.TextChoices):
        ULTRABULLET = "ultrabullet", "UltraBullet"
        BULLET = "bullet", "Bullet"
        BLITZ = "blitz", "Blitz"
        RAPID = "rapid", "Rapid"
        CLASSICAL = "classical", "Classical"
        CORRESPONDENCE = "correspondence", "Correspondence"
        UNKNOWN = "unknown", "Unknown"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")

    source = models.CharField(max_length=20, choices=Source.choices)
    lichess_game_id = models.CharField(max_length=20, null=True, blank=True)
    pgn_import = models.ForeignKey(
        "imports.PGNImport",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="games",
    )

    # Players
    white_username = models.CharField(max_length=100, blank=True, default="")
    black_username = models.CharField(max_length=100, blank=True, default="")
    user_color = models.CharField(max_length=5, choices=Color.choices)

    # Ratings
    white_rating = models.IntegerField(null=True, blank=True)
    black_rating = models.IntegerField(null=True, blank=True)
    user_rating = models.IntegerField(null=True, blank=True)
    opponent_rating = models.IntegerField(null=True, blank=True)

    # Result
    result = models.CharField(max_length=5, choices=Result.choices)
    user_result = models.CharField(max_length=4, choices=UserResult.choices)
    termination = models.CharField(max_length=20, choices=Termination.choices, default=Termination.OTHER)

    # Time control
    time_control = models.CharField(max_length=20, blank=True, default="")
    time_control_category = models.CharField(
        max_length=20,
        choices=TimeControlCategory.choices,
        default=TimeControlCategory.UNKNOWN,
    )
    initial_time = models.IntegerField(null=True, blank=True)  # seconds
    increment = models.IntegerField(default=0)  # seconds

    # Opening
    opening_name = models.CharField(max_length=200, blank=True, default="")
    opening_eco = models.CharField(max_length=10, blank=True, default="")

    # Raw PGN
    pgn = models.TextField()

    # Timestamps
    played_at = models.DateTimeField()
    imported_at = models.DateTimeField(auto_now_add=True)

    analysis_complete = models.BooleanField(default=False)

    class Meta:
        ordering = ["-played_at"]
        indexes = [
            models.Index(fields=["user", "-played_at"]),
            models.Index(fields=["user", "user_result"]),
            models.Index(fields=["user", "time_control_category"]),
            models.Index(fields=["user", "user_color"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lichess_game_id"],
                condition=models.Q(lichess_game_id__isnull=False),
                name="unique_user_lichess_game",
            )
        ]

    def __str__(self):
        return f"{self.white_username} vs {self.black_username} ({self.played_at.date()})"


class Move(models.Model):
    class Color(models.TextChoices):
        WHITE = "white", "White"
        BLACK = "black", "Black"

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="moves")
    ply = models.PositiveIntegerField()  # 1-indexed half-move number (1=white's first, 2=black's first, ...)
    move_number = models.PositiveIntegerField()  # Chess move number (1, 1, 2, 2, ...)
    color = models.CharField(max_length=5, choices=Color.choices)

    san = models.CharField(max_length=10)  # e.g., "Nf3", "O-O"
    uci = models.CharField(max_length=5)   # e.g., "g1f3", "e1g1"

    fen_before = models.TextField()
    fen_after = models.TextField()

    # Clock data (from PGN %clk annotations)
    clock_time_remaining = models.FloatField(null=True, blank=True)  # seconds remaining
    time_spent = models.FloatField(null=True, blank=True)            # seconds used on this move

    class Meta:
        ordering = ["ply"]
        unique_together = [["game", "ply"]]

    def __str__(self):
        return f"Move {self.move_number}{'.' if self.color == 'white' else '...'} {self.san}"
