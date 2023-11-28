from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from accounts.models import CustomUser


def sign_up(request):
    if request.method == "GET":
        return render(request, "signup.html")

    email = request.POST["email"]
    password1 = request.POST["password1"]
    password2 = request.POST["password2"]

    if password1 != password2:
        return render(request, "signup.html", {"error": "Passwords do not match"})

    try:
        user = CustomUser.objects.create(
            email=email,
            is_superuser=False,
            is_staff=False,
            is_active=True,
        )
        user.set_password(password1)
        user.save()
        login(request, user)
        print("User successfully registered. Redirecting now.")
        return redirect("/overview")
    except Exception as e:
        if settings.DEBUG:
            return render(request, "signup.html", {"error": str(e)})
        else:
            return render(
                request,
                "signup.html",
                {"error": "There was a problem registering your account"},
            )


def sign_in(request):
    if request.method == "GET":
        return render(request, "signin.html")

    email = request.POST["email"]
    password = request.POST["password"]
    user = authenticate(request, email=email, password=password)

    if user is None:
        return render(request, "signin.html", {"error": "Invalid username or password"})

    login(request, user)
    return redirect("/overview")


def sign_out(request):
    logout(request)
    return redirect("/account/signin")
