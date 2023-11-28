from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("signin", views.sign_in, name="signin"),
    path("signup", views.sign_up, name="signup"),
]
