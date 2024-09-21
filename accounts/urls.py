from django.urls import path
from accounts import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
    path('signup/', views.Signup, name='signup'),
    path('profile/', views.Profile, name='profile'),
    path('callback/', views.Callback, name='callback'),
]