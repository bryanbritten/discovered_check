from django.contrib import admin

from .models import LichessSync, PGNImport


@admin.register(PGNImport)
class PGNImportAdmin(admin.ModelAdmin):
    list_display = ["filename", "user", "status", "total_games", "processed_games", "created_at"]
    list_filter = ["status"]
    readonly_fields = ["created_at", "completed_at"]


@admin.register(LichessSync)
class LichessSyncAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "games_synced", "last_synced_at"]
    readonly_fields = ["last_synced_at", "started_at"]
