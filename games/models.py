from django.db import models

from accounts.models import CustomUser

class Opening(models.Model):
    eco = models.CharField(max_length=3)
    name = models.CharField(max_length=255)
    notation = models.CharField(max_length=255)
    ply = models.IntegerField()

class Game(models.Model):
    # TODO: get a full list of game status choices for enumeration
    GAME_STATUS_CHOICES = [
        ('mate', 'Checkmate'),
        ('draw', 'Draw'),
        ('resign', 'Resignation'),
        ('stalemate', 'Stalemate'),
        ('timeout', 'Timeout'),
    ]

    SPEED_CHOICES = [
        ('blitz', 'Blitz'),
        ('bullet', 'Bullet'),
        ('ultrabullet', 'Ultra Bullet'),
        ('classical', 'Classical'),
        ('correspondence', 'Correspondence'),
        ('rapid', 'Rapid'),
    ]

    PERF_CHOICES = [
        ('blitz', 'Blitz'),
        ('bullet', 'Bullet'),
        ('ultrabullet', 'Ultra Bullet'),
        ('classical', 'Classical'),
        ('correspondence', 'Correspondence'),
        ('rapid', 'Rapid'),
        ('chess960', 'Chess960'),
        ('crazyhouse', 'Crazyhouse'),
        ('antichess', 'Antichess'),
        ('atomic', 'Atomic'),
        ('horde', 'Horde'),
        ('kingOfTheHill', 'King of the Hill'),
        ('racingKings', 'Racing Kings'),
        ('threeCheck', 'Three-check'),
    ]

    COLORS = [
        ('black', 'Black'),
        ('white', 'White'),
    ]

    id = models.CharField(max_length=12, primary_key=True)
    game_id = models.CharField(max_length=8)
    rated = models.BooleanField()
    variant = models.CharField(max_length=255)
    speed = models.CharField(max_length=20, choices=SPEED_CHOICES)
    perf = models.CharField(max_length=20, choices=PERF_CHOICES)
    status = models.CharField(max_length=255)
    white_player = models.CharField(max_length=255)
    white_rating_start = models.SmallIntegerField()
    white_rating_end = models.SmallIntegerField()
    black_player = models.CharField(max_length=255)
    black_rating_start = models.SmallIntegerField()
    black_rating_end = models.SmallIntegerField()
    winner = models.CharField(max_length=5, choices=COLORS, blank=True, null=True)
    opening = models.ForeignKey(Opening, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField()
    last_move_at = models.DateTimeField()
    initial_clock = models.SmallIntegerField()
    increment = models.SmallIntegerField()
    total_time = models.SmallIntegerField()

class Move(models.Model):
    COLORS = [
        ('black', 'Black'),
        ('white', 'White'),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    move_number = models.SmallIntegerField()
    move = models.CharField(max_length=10)
    color = models.CharField(max_length=5, choices=COLORS)
    clock_start = models.SmallIntegerField(blank=True, null=True)
    clock_end = models.SmallIntegerField(blank=True, null=True)
    time_spent = models.SmallIntegerField(blank=True, null=True)

class Player(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    platform = models.CharField(max_length=10, choices=[('lichess', 'Lichess'), ('chesscom', 'Chess.com')])
    title = models.CharField(max_length=255, blank=True, null=True) # todo: make this a choice field
    blitz_games = models.IntegerField(default=0)
    blitz_rating = models.SmallIntegerField(default=0)
    bullet_games = models.IntegerField(default=0)
    bullet_rating = models.SmallIntegerField(default=0)
    ultra_bullet_games = models.IntegerField(default=0)
    ultra_bullet_rating = models.SmallIntegerField(default=0)
    rapid_games = models.IntegerField(default=0)
    rapid_rating = models.SmallIntegerField(default=0)
    puzzles_completed = models.IntegerField(default=0)
    puzzles_rating = models.SmallIntegerField(default=0)
    classical_games = models.IntegerField(default=0)
    classical_rating = models.SmallIntegerField(default=0)
    member_since = models.DateTimeField(blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    is_disabled = models.BooleanField(default=False)
    violated_tos = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)