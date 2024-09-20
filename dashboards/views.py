from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect

def redirect_to_overview(request):
    return redirect('overview')

def overview(request):
    context = {
        "latest_question_list": [],
    }
    return render(request, 'dashboards/overview.html', context)

def time(request):
    return HttpResponse(f"The time is {datetime.now().isoformat()}") 

def tactics(request):
    return HttpResponse("This page will eventually show analyses of tactics for your games.")

def openings(request):
    return HttpResponse("This page will eventually show analyses of openings for your games.")