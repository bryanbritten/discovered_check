from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/games/", include("apps.games.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/imports/", include("apps.imports.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
