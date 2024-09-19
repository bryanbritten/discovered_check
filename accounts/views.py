from django.shortcuts import redirect, render

def login(request):
    return render(request, 'accounts/login.html')

def logout(request):
    print('logging out the user')
    return redirect('accounts:login')

def signup(request):
    return render(request, 'accounts/signup.html')

def profile(request):
    return render(request, 'accounts/profile.html')