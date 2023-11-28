from django.db import models
from games.enums import Color, TimeClass, TournamentStatus
from players.models import Player


class Tournament(models.Model):
    name = models.TextField()
    url = models.URLField(unique=True)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(
        Player,
        to_field="username",
        db_column="creator",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    status = models.CharField(max_length=15, choices=TournamentStatus.choices)
    finish_time = models.DateTimeField(blank=True, null=True)
    type = models.CharField(max_length=100)
    rules = models.CharField(max_length=50)
    time_class = models.CharField(max_length=5, choices=TimeClass.choices)
    time_control = models.CharField(max_length=10)
    is_rated = models.BooleanField(default=True)
    is_official = models.BooleanField(default=False)
    is_invite_only = models.BooleanField(default=False)
    initial_group_size = models.IntegerField()
    user_advance_count = models.SmallIntegerField()
    use_tiebreak = models.BooleanField(default=True)
    allow_vacation = models.BooleanField(default=False)
    winner_places = models.SmallIntegerField(default=1)
    registered_user_count = models.IntegerField()
    games_per_opponent = models.SmallIntegerField()
    total_rounds = models.SmallIntegerField()
    concurrent_games_per_opponent = models.SmallIntegerField()

    def __str__(self):
        return f"{self.name} ({self.id})"


class Game(models.Model):
    game_id = models.CharField(max_length=50, unique=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(blank=True, null=True)
    time_control = models.CharField(max_length=10)
    time_class = models.CharField(max_length=5, choices=TimeClass.choices)
    opening = models.CharField(max_length=255, blank=True, null=True)
    result = models.CharField(max_length=5, blank=True, null=True)
    outcome = models.CharField(max_length=255, blank=True, null=True)
    tournament = models.ForeignKey(
        Tournament,
        db_column="tournament",
        related_name="tournaments",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    white_player = models.ForeignKey(
        Player,
        to_field="username",
        db_column="white_player",
        related_name="games_as_white",
        null=True,
        on_delete=models.SET_NULL,
    )
    white_elo = models.SmallIntegerField()
    white_accuracy = models.FloatField(blank=True, null=True)
    black_player = models.ForeignKey(
        Player,
        to_field="username",
        db_column="black_player",
        related_name="games_as_black",
        null=True,
        on_delete=models.SET_NULL,
    )
    black_elo = models.SmallIntegerField()
    black_accuracy = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.game_id


class Move(models.Model):
    game_id = models.ForeignKey(
        Game,
        to_field="game_id",
        db_column="game_id",
        related_name="moves",
        on_delete=models.CASCADE,
    )
    move_num = models.SmallIntegerField()
    move = models.CharField(max_length=10)
    color = models.CharField(max_length=5, choices=Color.choices)
    player = models.ForeignKey(
        Player,
        to_field="username",
        related_name="moves",
        db_column="player",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game_id", "move_num", "color"],
                name="unique_game_id_move_num_color_constraint",
            )
        ]

    def __str__(self):
        if self.color == "black":
            return f"{self.move_num}... {self.move}"
        else:
            return f"{self.move_num}. {self.move}"
