from django.urls import path
from dashboards import views

app_name = 'dashboards'
urlpatterns = [
    path('', views.root, name='root'),
    path('overview/', views.overview, name='overview'),
    path('time/', views.time, name='time'),
    path('tactics/', views.tactics, name='tactics'),
    path('openings/', views.openings, name='openings'),
    path('profile/', views.profile, name='profile'),
    path('fetch_games_from_api/', views.fetch_games_from_api, name='fetch_games_from_api'),
]