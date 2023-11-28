from django.urls import path

from . import views

urlpatterns = [
    path("", views.default_landing, name="default_landing"),
    path("overview", views.overview, name="overview"),
]
