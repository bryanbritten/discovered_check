from django.db import models

from players.enums import PlayerStatus, Title


class Country(models.Model):
    class Meta:
        verbose_name = "country"
        verbose_name_plural = "countries"

    code = models.CharField(
        max_length=2,
        primary_key=True,
        db_column="code",
    )
    name = models.CharField(max_length=60, unique=True)
    url = models.URLField(unique=True)

    def __str__(self):
        return self.code


class Player(models.Model):
    username = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=3, choices=Title.choices)
    status = models.CharField(max_length=30, choices=PlayerStatus.choices)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey(
        Country,
        related_name="players",
        db_column="country",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    fide_rating = models.SmallIntegerField(blank=True, null=True)
