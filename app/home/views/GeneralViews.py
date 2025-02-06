from django.shortcuts import render, redirect
from django.contrib.auth import login,logout, authenticate
from django.contrib.auth.models import Group
from home.enum.GroupEnum import GroupEnum
from django.http import JsonResponse
import logging
from home.forms.CreateUserForm import CreateUserForm
from home.email.UserMail import UserMail
from home.service.FailedLoginAttemptService import FailedLoginAttemptService

def home(request):
    return render(request, "home.html", {"title": "Accueil"})


def create_account(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name=GroupEnum.USER_STANDARD.name)
            group.user_set.add(user)
            UserMail(user).send_welcome_email()
            return redirect('login')
    else:
        form = CreateUserForm()
    return render(request, 'Account/create_account.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        failed_login_attempt_service = FailedLoginAttemptService(request, username)
        if user is not None:
            login(request, user)
            failed_login_attempt_service.purge()
            return redirect('home')
        # wrong password
        failed_login_attempt_service.add_or_create_failed_login_attempt()
        if(failed_login_attempt_service.is_timeout()) :
            return render(request, '429.html', status=429)
    
    return render(request, 'Account/login.html')

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')




