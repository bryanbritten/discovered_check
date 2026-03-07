from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import LichessToken, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "lichess_username", "lichess_id", "is_active", "date_joined"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Lichess", {"fields": ("lichess_id", "lichess_username", "avatar_url")}),
    )


@admin.register(LichessToken)
class LichessTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "token_type", "scope", "created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]
