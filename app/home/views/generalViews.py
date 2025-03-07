from django.shortcuts import render, redirect
from django.contrib.auth import login,logout, authenticate
from django.contrib.auth.models import Group
from home.models.User import User
from home.enum.GroupEnum import GroupEnum
from django.http import JsonResponse
import logging
from home.forms.CreateUserForm import CreateUserForm
from home.forms.UserResetPasswordForm import UserResetPasswordForm
from home.email.UserMail import UserMail
from home.service.FailedLoginAttemptService import FailedLoginAttemptService
from django.core.exceptions import ValidationError
from home.service.ConfirmationUserService import ConfirmationUserService
from home.utils.url import get_full_url
from home.decorator.detectNotConfirmedAccount import detect_not_confirmed_account
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
from home.service.ResetPasswordService import ResetPasswordService
from home.forms.UserPasswordForm import UserPasswordForm
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
                    messages.info(request, "Compte créé")
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


@require_http_methods(['POST'])
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

@require_http_methods(['GET', 'POST'])
@ratelimit(key='ip', rate='3/m', method='POST', block=True)
def send_reset_password(request):
    logger = logging.getLogger('home')
    if request.method == 'POST':
        form = UserResetPasswordForm(request.POST)
        try:
            if form.is_valid():
                user = form.cleaned_data["identifier"]  # Contient l'instance User
                logger.info("reset password for user : " + str(user))
                url = get_full_url(ResetPasswordService(user).generation_uri())
                UserMail(user).send_reset_password_email(url)
        except Exception as e:
            logger.error(f"reset password error : {e}")
        messages.info(request, "Email envoyé si l'addresse existe")
    else : 
        form = UserResetPasswordForm()
    return render(request, 'Html/Account/send_reset_password.html', {'form':form})

@require_http_methods(['GET', 'POST'])
@ratelimit(key='ip', rate='3/m', method='POST', block=True)
def token_validation_reset_password(request, uuid_user:str, token_reinitialisation:str):
    logger = logging.getLogger('home')
    user = None
    try:
        user = User.objects.get(uuid=uuid_user)
    except User.DoesNotExist:
        pass
    if user is None :
        return render(request, 'Html/General/404.html', status=404)
    
    is_valid = False
    reset_password_service = ResetPasswordService(user)
    try: 
        reset_password_service.verification_token(token_reinitialisation)
        is_valid = True
    except Exception as e:
        logger.error(f"token validation error : {e}")
        
    if not is_valid:
        return render(request, 'Html/General/404.html', status=404)
    
    
    if request.method == 'POST':
        form = UserPasswordForm(request.POST,instance=user)
        if form.is_valid():
            try:
                user = form.save()
                logger.info(f"User password modified{user.username}")
                messages.info(request, "Mot de passe modifié")
                UserMail(user).send_password_changed_email()
                reset_password_service.clean()
                return redirect('login')
            except Exception as e:
                logger.error(e)
    if request.method == 'GET':
        form = UserPasswordForm(instance=user)
    return render(request, 'Html/Account/reset_password.html', {'form':form})