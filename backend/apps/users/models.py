from django.contrib.auth.models import AbstractUser
from django.db import models


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
