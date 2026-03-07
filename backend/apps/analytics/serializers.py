from rest_framework import serializers

from .models import GameAnalysis, TacticsOpportunity


class TacticsOpportunitySerializer(serializers.ModelSerializer):
    game_id = serializers.UUIDField(source="game.id", read_only=True)
    lichess_game_id = serializers.CharField(source="game.lichess_game_id", read_only=True)
    played_at = serializers.DateTimeField(source="game.played_at", read_only=True)
    move_number = serializers.IntegerField(source="move.move_number", read_only=True)
    move_color = serializers.CharField(source="move.color", read_only=True)

    class Meta:
        model = TacticsOpportunity
        fields = [
            "id",
            "game_id",
            "lichess_game_id",
            "played_at",
            "tactic_type",
            "missed",
            "best_move_uci",
            "played_move_uci",
            "attacking_piece",
            "attacking_square",
            "targets",
            "fen",
            "description",
            "move_number",
            "move_color",
        ]


class GameAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameAnalysis
        fields = [
            "tactics_opportunities_count",
            "tactics_missed_count",
            "avg_time_per_move",
            "median_time_per_move",
            "max_time_per_move",
            "total_time_used",
            "time_pressure_moves_count",
            "analyzed_at",
        ]
