from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from accounts.models import AuthToken
from games.services import fetch_games_from_api_service, fetch_games_from_db_service

@login_required
def root(request):
    return redirect('dashboards:overview')

@login_required
def overview(request):
    games = fetch_games_from_db_service(username='bbritten')
    context = {
        "games": games,
        "num_games": len(games),
    }
    return render(request, 'dashboards/overview.html', context)

@login_required
def time(request):
    return HttpResponse(f"The time is {datetime.now().isoformat()}") 

@login_required
def tactics(request):
    return HttpResponse("This page will eventually show analyses of tactics for your games.")

@login_required
def openings(request):
    return HttpResponse("This page will eventually show analyses of openings for your games.")

@require_POST
@login_required
def fetch_games_from_api(request):
    token = request.user.authtoken.access_token
    fetch_games_from_api_service(username='bbritten', token=token)
    return redirect('dashboards:overview')