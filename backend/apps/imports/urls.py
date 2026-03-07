from django.urls import path

from . import views

urlpatterns = [
    path("pgn/", views.pgn_upload, name="pgn-upload"),
    path("pgn/list/", views.PGNImportListView.as_view(), name="pgn-list"),
    path("pgn/<int:pk>/", views.pgn_import_detail, name="pgn-detail"),
    path("lichess/sync/", views.lichess_sync, name="lichess-sync"),
    path("lichess/sync/status/", views.lichess_sync_status, name="lichess-sync-status"),
]
