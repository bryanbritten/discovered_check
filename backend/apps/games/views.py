from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Game
from .serializers import GameDetailSerializer, GameListSerializer


class GameListView(generics.ListAPIView):
    serializer_class = GameListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Game.objects.filter(user=self.request.user)

        color = self.request.query_params.get("color")
        if color in ("white", "black"):
            qs = qs.filter(user_color=color)

        result = self.request.query_params.get("result")
        if result in ("win", "loss", "draw"):
            qs = qs.filter(user_result=result)

        tc = self.request.query_params.get("time_control_category")
        if tc:
            qs = qs.filter(time_control_category=tc)

        source = self.request.query_params.get("source")
        if source in ("lichess", "pgn_import"):
            qs = qs.filter(source=source)

        return qs


class GameDetailView(generics.RetrieveAPIView):
    serializer_class = GameDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Game.objects.filter(user=self.request.user).prefetch_related("moves")
