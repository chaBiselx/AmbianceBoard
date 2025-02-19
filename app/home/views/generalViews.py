from django.shortcuts import render, redirect
from django.contrib.auth import login,logout, authenticate
from django.contrib.auth.models import Group
from home.models.User import User
from home.enum.GroupEnum import GroupEnum
from django.http import JsonResponse
import logging
from home.forms.CreateUserForm import CreateUserForm
from home.email.UserMail import UserMail
from home.service.FailedLoginAttemptService import FailedLoginAttemptService
from django.core.exceptions import ValidationError
from home.service.ConfirmationUserService import ConfirmationUserService
from home.utils.url import get_full_url
from home.decorator.detectNotConfirmedAccount import detect_not_confirmed_account
from django.views.decorators.http import require_http_methods

@detect_not_confirmed_account()
def home(request):
    return render(request, "Html/General/home.html", {"title": "Accueil"})


def create_account(request):
    logger = logging.getLogger('home')
    errors = []
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                group = Group.objects.get(name=GroupEnum.USER_STANDARD.name)
                group.user_set.add(user)
                UserMail(user).send_welcome_email()
                try:
                    confirmation_user_service = ConfirmationUserService(user)
                    url = get_full_url(confirmation_user_service.generation_uri())
                    UserMail(user).send_account_confirmation_email(url)
                except Exception as e:
                    logger.error(e)
                logger.info(f"User {user.username} created")
                return redirect('login')
            except Exception as e:
                logger.error(e)
    else:
        form = CreateUserForm()
    return render(request, 'Html/Account/create_account.html', {'form': form, 'errors':errors})

def login_view(request):
    context = {}
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
            return render(request, 'Html/General/429.html', status=429)
    
    return render(request, 'Html/Account/login.html', context)

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')


# @require_http_methods(['POST'])
def resend_email_confirmation(request) -> JsonResponse:
    logger = logging.getLogger('home')
    if request.user.is_authenticated and request.method == 'POST' and request.user.isConfirmed == False :
        try:
            confirmation_user_service = ConfirmationUserService(request.user)
            url = get_full_url(confirmation_user_service.generation_uri())
            UserMail(request.user).send_account_confirmation_email(url)
            return JsonResponse({"message": "email send"}, status=200)
        except Exception as e:
            logger.error(f"resend confirmation error : {e}")
            return JsonResponse({"error": "Cannot send email"}, status=500)
    return JsonResponse({"error": "Not acceptable."}, status=406)
