from django.contrib import admin

from .models import Game, Move


class MoveInline(admin.TabularInline):
    model = Move
    extra = 0
    readonly_fields = ["ply", "move_number", "color", "san", "uci", "clock_time_remaining", "time_spent"]
    can_delete = False
    max_num = 0


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "white_username",
        "black_username",
        "user_color",
        "user_result",
        "time_control_category",
        "played_at",
        "analysis_complete",
    ]
    list_filter = ["user_result", "time_control_category", "user_color", "source", "analysis_complete"]
    search_fields = ["white_username", "black_username", "lichess_game_id"]
    readonly_fields = ["id", "imported_at"]
    inlines = [MoveInline]
