from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from games.services import fetch_games_from_api_service, fetch_games_from_db_service

def redirect_to_overview(request):
    return redirect('dashboards:overview')

@login_required
def overview(request):
    games = fetch_games_from_db_service(username='bbritten')
    context = {
        "games": games,
        "num_games": len(games),
    }
    return render(request, 'dashboards/overview.html', context)

def time(request):
    return HttpResponse(f"The time is {datetime.now().isoformat()}") 

def tactics(request):
    return HttpResponse("This page will eventually show analyses of tactics for your games.")

def openings(request):
    return HttpResponse("This page will eventually show analyses of openings for your games.")

@require_POST
def fetch_games_from_api(request):
    fetch_games_from_api_service(username='bbritten')
    return redirect('dashboards:overview')