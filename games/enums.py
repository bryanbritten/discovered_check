from django.db import models


class TimeClass(models.TextChoices):
    LIVE = "LIVE", "Live"
    DAILY = "DAILY", "Daily"


class TournamentStatus(models.TextChoices):
    REGISTRATION = "REGISTRATION", "Registration"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    FINISHED = "FINISHED", "Finished"


class Color(models.TextChoices):
    BLACK = "BLACK", "Black"
    WHITE = "WHITE", "White"
