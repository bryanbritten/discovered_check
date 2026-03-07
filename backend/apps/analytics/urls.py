from django.urls import path

from . import views

urlpatterns = [
    path("overview/", views.overview, name="analytics-overview"),
    path("tactics/", views.TacticsListView.as_view(), name="analytics-tactics"),
    path("time/", views.time_analysis, name="analytics-time"),
]
