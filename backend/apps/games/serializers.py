from rest_framework import serializers

from .models import Game, Move


class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Move
        fields = [
            "ply",
            "move_number",
            "color",
            "san",
            "uci",
            "fen_before",
            "fen_after",
            "clock_time_remaining",
            "time_spent",
        ]


class GameListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""

    class Meta:
        model = Game
        fields = [
            "id",
            "source",
            "lichess_game_id",
            "white_username",
            "black_username",
            "user_color",
            "user_rating",
            "opponent_rating",
            "result",
            "user_result",
            "termination",
            "time_control",
            "time_control_category",
            "opening_name",
            "opening_eco",
            "played_at",
            "analysis_complete",
        ]


class GameDetailSerializer(GameListSerializer):
    """Full serializer including moves."""

    moves = MoveSerializer(many=True, read_only=True)

    class Meta(GameListSerializer.Meta):
        fields = GameListSerializer.Meta.fields + ["pgn", "moves"]
