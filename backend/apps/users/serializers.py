from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "lichess_id", "lichess_username", "avatar_url"]
        read_only_fields = fields
