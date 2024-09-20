from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('dashboards/', include('dashboards.urls')),
    path('admin/', admin.site.urls),
]
