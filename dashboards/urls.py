from django.urls import path
from dashboards import views

app_name = 'dashboards'
urlpatterns = [
    path('', views.redirect_to_overview, name='redirect_to_overview'),
    path('overview/', views.overview, name='overview'),
    path('time/', views.time, name='time'),
    path('tactics/', views.tactics, name='tactics'),
    path('openings/', views.openings, name='openings'),
    path('fetch_games_from_api/', views.fetch_games_from_api, name='fetch_games_from_api'),
]