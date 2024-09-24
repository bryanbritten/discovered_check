from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from accounts.models import AuthToken
from games.services import fetch_games_from_api_service, fetch_games_from_db_service

@login_required
def root(request):
    """
    A user's session should persist as long as they are regularly using the app.
    To achieve this, request.session.modified can be set to True whenever the user
    accesses the root URL of the app, which should happen every time they launch the app.
    """
    request.session.modified = True
    return redirect('dashboards:overview')

@login_required
def overview(request):
    games = fetch_games_from_db_service(username='bbritten')
    context = {
        "username": request.user.username,
        "games": games,
        "num_games": len(games),
    }
    return render(request, 'dashboards/overview.html', context)

@login_required
def time(request):
    cur_time = datetime.now().isoformat()
    context = {
        "cur_time": cur_time,
    }
    return render(request, 'dashboards/time.html', context)

@login_required
def tactics(request):
    context = {}
    return render(request, 'dashboards/tactics.html', context)

@login_required
def openings(request):
    context = {}
    return render(request, 'dashboards/openings.html', context)

@require_POST
@login_required
def fetch_games_from_api(request):
    token = request.user.authtoken.access_token
    fetch_games_from_api_service(username='bbritten', token=token)
    return redirect('dashboards:overview')

@login_required
def profile(request):
    context = {
        "user": request.user,
    }
    return render(request, 'dashboards/profile.html', context)