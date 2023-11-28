from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


@login_required
def default_landing(request):
    return redirect("/overview")


@login_required
def overview(request):
    return render(request, "overview.html")
