from django.http import HttpResponse


def profile(request):
    return HttpResponse("this is a user profile")
