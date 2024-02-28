from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def index(request):
    return render(request, 'main/index.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user_data = authenticate(request, username=username, password=password)
        if user_data:
            login(request, user_data)
            return redirect('user')
        else:
            error_message = 'Invalid login credentials.'
            return render(request, 'main/error_login.html', {'error_message': error_message})

    else:
        user_data = User()
        return render(request, 'main/user_login.html', {'user_data': user_data})

