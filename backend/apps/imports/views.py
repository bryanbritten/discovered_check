from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import LichessSync, PGNImport
from .serializers import LichessSyncSerializer, PGNImportSerializer


class PGNImportListView(generics.ListAPIView):
    serializer_class = PGNImportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PGNImport.objects.filter(user=self.request.user)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pgn_upload(request):
    """
    Upload a PGN file. Parsing happens synchronously for now.
    A future iteration can offload to Celery.
    """
    from .pgn_parser import parse_pgn_string
    from .tactics_detector import analyze_game_tactics
    from apps.games.models import Game

    file = request.FILES.get("file")
    if not file:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

    if not file.name.endswith(".pgn"):
        return Response({"error": "Only .pgn files are accepted."}, status=status.HTTP_400_BAD_REQUEST)

    pgn_import = PGNImport.objects.create(
        user=request.user,
        filename=file.name,
        file=file,
        status=PGNImport.Status.PROCESSING,
    )

    try:
        pgn_text = pgn_import.file.read().decode("utf-8", errors="replace")
        saved, failed = parse_pgn_string(pgn_text, request.user, pgn_import)

        # Run tactics detection on newly imported games
        new_games = Game.objects.filter(pgn_import=pgn_import)
        pgn_import.total_games = saved + failed
        pgn_import.processed_games = saved
        pgn_import.failed_games = failed

        for game in new_games:
            try:
                analyze_game_tactics(game)
            except Exception:
                pass  # Don't fail the whole import if tactics detection errors

        pgn_import.status = PGNImport.Status.COMPLETE
        pgn_import.completed_at = timezone.now()
        pgn_import.save()

        return Response(PGNImportSerializer(pgn_import).data, status=status.HTTP_201_CREATED)

    except Exception as exc:
        pgn_import.status = PGNImport.Status.FAILED
        pgn_import.error_message = str(exc)
        pgn_import.save(update_fields=["status", "error_message"])
        return Response(
            {"error": "Import failed.", "detail": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pgn_import_detail(request, pk):
    try:
        pgn_import = PGNImport.objects.get(pk=pk, user=request.user)
    except PGNImport.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(PGNImportSerializer(pgn_import).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def lichess_sync(request):
    """
    Trigger a Lichess game sync for the authenticated user.
    Fetches games from Lichess and runs the full import + analysis pipeline.
    """
    from .lichess_client import fetch_user_games
    from .pgn_parser import parse_pgn_string
    from .tactics_detector import analyze_game_tactics
    from apps.games.models import Game

    user = request.user

    try:
        token = user.lichess_token
    except Exception:
        return Response(
            {"error": "No Lichess token found. Please log in with Lichess first."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    sync, _ = LichessSync.objects.get_or_create(user=user)

    if sync.status == LichessSync.Status.SYNCING:
        return Response(
            {"error": "A sync is already in progress."},
            status=status.HTTP_409_CONFLICT,
        )

    sync.status = LichessSync.Status.SYNCING
    sync.started_at = timezone.now()
    sync.error_message = ""
    sync.save(update_fields=["status", "started_at", "error_message"])

    try:
        pgn_text = fetch_user_games(
            access_token=token.access_token,
            username=user.lichess_username or user.username,
            since=sync.since_timestamp,
            max_games=500,
        )

        saved, failed = parse_pgn_string(pgn_text, user, pgn_import=None)

        # Run tactics on newly synced games (those without a pgn_import)
        new_games = Game.objects.filter(
            user=user,
            source="lichess",
            analysis_complete=True,
            pgn_import__isnull=True,
        ).order_by("-imported_at")[:saved]

        for game in new_games:
            try:
                analyze_game_tactics(game)
            except Exception:
                pass

        # Update cursor to now (milliseconds)
        import time
        sync.since_timestamp = int(time.time() * 1000)
        sync.games_synced += saved
        sync.last_synced_at = timezone.now()
        sync.status = LichessSync.Status.IDLE
        sync.save()

        return Response(LichessSyncSerializer(sync).data)

    except Exception as exc:
        sync.status = LichessSync.Status.FAILED
        sync.error_message = str(exc)
        sync.save(update_fields=["status", "error_message"])
        return Response(
            {"error": "Sync failed.", "detail": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def lichess_sync_status(request):
    sync, _ = LichessSync.objects.get_or_create(user=request.user)
    return Response(LichessSyncSerializer(sync).data)
