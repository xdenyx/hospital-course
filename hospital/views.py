from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import LoginForm 

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, "Неправильне ім'я користувача або пароль")
    else:
        form = LoginForm()
    
    return render(request, 'spa/login.html', {'form': form})

def logout_view(request):
    """Вихід з системи"""
    logout(request)
    return redirect('login')


@login_required
def index_view(request):
    """Головна сторінка системи (віддає SPA)"""
    return render(request, 'spa/index.html')