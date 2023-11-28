from django.http import HttpResponse


def login(request):
    return HttpResponse("This is the login page")


def signup(request):
    return HttpResponse("This is the signup page")
