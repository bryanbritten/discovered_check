import secrets
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    lichess_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    lichess_username = models.CharField(max_length=50, null=True, blank=True)
    avatar_url = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.lichess_username or self.username


class LichessToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="lichess_token")
    access_token = models.TextField()
    token_type = models.CharField(max_length=20, default="Bearer")
    scope = models.TextField(blank=True, default="")
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Token for {self.user}"


class UserSession(models.Model):
    """
    Persistent login session. A secure token is stored in an httpOnly cookie so
    the user can obtain fresh JWTs without re-authorizing with Lichess.
    """

    LIFETIME = timedelta(days=365)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    @classmethod
    def create_for_user(cls, user: "User") -> "UserSession":
        cls.objects.filter(user=user, expires_at__lt=timezone.now()).delete()
        return cls.objects.create(
            user=user,
            token=secrets.token_urlsafe(48),
            expires_at=timezone.now() + cls.LIFETIME,
        )

    def is_valid(self) -> bool:
        return timezone.now() < self.expires_at

    def touch(self) -> None:
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at"])

    def __str__(self):
        return f"Session for {self.user} (expires {self.expires_at.date()})"
