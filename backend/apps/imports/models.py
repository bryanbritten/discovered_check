from django.db import models

from apps.users.models import User


class PGNImport(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETE = "complete", "Complete"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pgn_imports")
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to="pgn_imports/%Y/%m/")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_games = models.IntegerField(null=True, blank=True)
    processed_games = models.IntegerField(default=0)
    failed_games = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.filename} ({self.user})"


class LichessSync(models.Model):
    class Status(models.TextChoices):
        IDLE = "idle", "Idle"
        SYNCING = "syncing", "Syncing"
        FAILED = "failed", "Failed"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="lichess_sync")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IDLE)
    games_synced = models.IntegerField(default=0)
    since_timestamp = models.BigIntegerField(null=True, blank=True)  # Lichess API cursor
    error_message = models.TextField(blank=True, default="")
    last_synced_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Sync for {self.user} ({self.status})"
