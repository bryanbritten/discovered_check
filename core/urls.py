from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("dashboard/", include("dashboards.urls")),
    path("profile/", include("players.urls")),
]
