from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("account/", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("", include("dashboards.urls")),
    path("profile/", include("players.urls")),
]
