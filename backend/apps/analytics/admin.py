from django.contrib import admin

from .models import GameAnalysis, MoveTimeCategory, TacticsOpportunity


@admin.register(TacticsOpportunity)
class TacticsOpportunityAdmin(admin.ModelAdmin):
    list_display = ["game", "tactic_type", "missed", "attacking_piece", "attacking_square"]
    list_filter = ["tactic_type", "missed"]


@admin.register(GameAnalysis)
class GameAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        "game",
        "tactics_opportunities_count",
        "tactics_missed_count",
        "avg_time_per_move",
        "analyzed_at",
    ]
    readonly_fields = ["analyzed_at"]
