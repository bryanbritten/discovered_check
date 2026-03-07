from rest_framework import serializers

from .models import LichessSync, PGNImport


class PGNImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PGNImport
        fields = [
            "id",
            "filename",
            "status",
            "total_games",
            "processed_games",
            "failed_games",
            "error_message",
            "created_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "total_games",
            "processed_games",
            "failed_games",
            "error_message",
            "created_at",
            "completed_at",
        ]


class LichessSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = LichessSync
        fields = [
            "status",
            "games_synced",
            "last_synced_at",
            "started_at",
            "error_message",
        ]
        read_only_fields = fields
