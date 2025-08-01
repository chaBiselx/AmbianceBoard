import uuid
from typing import Union
from django.shortcuts import render, redirect
from django.contrib.auth import login,logout, authenticate
from django.contrib.auth.models import Group
from django.http import JsonResponse, HttpRequest, HttpResponse
from main.models.User import User
from main.enum.GroupEnum import GroupEnum
from main.forms.CreateUserForm import CreateUserForm
from main.forms.UserResetPasswordForm import UserResetPasswordForm
from main.email.UserMail import UserMail
from main.service.FailedLoginAttemptService import FailedLoginAttemptService
from django.core.exceptions import ValidationError
from main.service.ConfirmationUserService import ConfirmationUserService
from main.utils.url import get_full_url
from main.decorator.detectNotConfirmedAccount import detect_not_confirmed_account
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from main.utils.ServerNotificationBuilder import ServerNotificationBuilder

from django_ratelimit.decorators import ratelimit
from main.service.ResetPasswordService import ResetPasswordService
from main.forms.UserPasswordForm import UserPasswordForm
from main.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.enum.ErrorMessageEnum import ErrorMessageEnum
from main.models.UserNotificationDismissal import UserNotificationDismissal
from main.models.GeneralNotification import GeneralNotification
from main.models.UserTier import UserTier
from main.utils.logger import logger



@detect_not_confirmed_account()
@require_http_methods(['GET'])
def home(request: HttpRequest) -> HttpResponse:
    """
    Vue de la page d'accueil.
    
    Affiche la page d'accueil principale de l'application.
    Redirige les utilisateurs non confirmés selon le décorateur.
    
    Args:
        request (HttpRequest): Requête HTTP
        
    Returns:
        HttpResponse: Page d'accueil rendue
    """
    return render(request, "Html/General/home.html", {"title": "Accueil"})


@require_http_methods(['GET'])
def legal_notice(request: HttpRequest) -> HttpResponse:
    """
    Vue de la page des mentions légales.
    
    Args:
        request (HttpRequest): Requête HTTP
        
    Returns:
        HttpResponse: Page des mentions légales rendue
    """
    return render(request, "Html/General/legal_notice.html", {"title": "Mention légal"})

@require_http_methods(['GET', 'POST'])
def create_account(request: HttpRequest) -> HttpResponse:
    """
    Vue de création de compte utilisateur.
    
    Gère la création d'un nouveau compte utilisateur avec :
    - Validation du formulaire
    - Attribution du groupe utilisateur standard
    - Envoi d'emails de bienvenue et de confirmation
    - Création du tier utilisateur
    - Gestion des erreurs
    
    Args:
        request (HttpRequest): Requête HTTP
        
    Returns:
        HttpResponse: Page de création de compte ou redirection vers login
    """
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
                    ServerNotificationBuilder(request).set_message(
                        "Un email de confirmation a été envoyé à votre adresse."
                    ).set_statut("info").send()
                except Exception as e:
                    logger.error(e)
                logger.info(f"User {user.username} created")
                UserTier.objects.create(
                    user=user,
                    tier_name='STANDARD'
                )
                return redirect('login')
            except Exception as e:
                logger.error(e)
    else:
        form = CreateUserForm()
    return render(request, 'Html/Account/create_account.html', {'form': form, 'errors':errors})

@require_http_methods(['GET', 'POST'])
def login_view(request: HttpRequest) -> HttpResponse:
    """
    Vue de connexion utilisateur.
    
    Gère l'authentification des utilisateurs avec :
    - Validation des identifiants
    - Gestion des tentatives de connexion échouées
    - Protection contre le brute force
    - Redirection vers la page d'accueil en cas de succès
    
    Args:
        request (HttpRequest): Requête HTTP
        
    Returns:
        HttpResponse: Page de connexion ou redirection, 
                     peut retourner une erreur 429 en cas de trop nombreuses tentatives
    """
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
            return render(request, HtmlDefaultPageEnum.ERROR_429.value, status=429)
    
    return render(request, 'Html/Account/login.html', context)

@require_http_methods(['GET'])
def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Vue de déconnexion utilisateur.
    
    Déconnecte l'utilisateur s'il est authentifié et redirige vers l'accueil.
    
    Args:
        request (HttpRequest): Requête HTTP
        
    Returns:
        HttpResponse: Redirection vers la page d'accueil
    """
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')

@login_required
@require_http_methods(['POST'])
@ratelimit(key='ip', rate='3/m', method='POST', block=True)
def resend_email_confirmation(request) -> JsonResponse:
    if request.user.is_authenticated and request.method == 'POST' and request.user.isConfirmed == False :
        try:
            confirmation_user_service = ConfirmationUserService(request.user)
            url = get_full_url(confirmation_user_service.generation_uri())
            UserMail(request.user).send_account_confirmation_email(url)
            return JsonResponse({"message": "email send"}, status=200)
        except Exception as e:
            logger.error(f"resend confirmation error : {e}")
            return JsonResponse({"error": "Cannot send email"}, status=500)
    return JsonResponse({"error": ErrorMessageEnum.NOT_ACCEPTABLE.value}, status=406)

@login_required
@require_http_methods(['POST'])
@ratelimit(key='ip', rate='3/m', method='POST', block=True)
def dismiss_general_notification(request, notification_uuid: uuid.UUID) -> JsonResponse:
    if request.method == 'POST':
        try:
            general_information = GeneralNotification.objects.get(uuid=notification_uuid)
            if not general_information:
                raise ValidationError("Notification not found")
            _,_ = UserNotificationDismissal.objects.get_or_create(
                user=request.user,
                notification_id=general_information.id
            )
            return JsonResponse({"message": "Notification dismissed"}, status=200)
        except Exception as e:
            logger.error(f"dismiss notification error : {e}")
            return JsonResponse({"error": "Cannot dismiss notification"}, status=500)
    return JsonResponse({"error": ErrorMessageEnum.NOT_ACCEPTABLE.value}, status=406)
            

@require_http_methods(['GET', 'POST'])
@ratelimit(key='ip', rate='3/m', method='POST', block=True)
def send_reset_password(request):
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
        ServerNotificationBuilder(request).set_message("Email envoyé si l'addresse existe").set_statut("info").send()
    else : 
        form = UserResetPasswordForm()
    return render(request, 'Html/Account/send_reset_password.html', {'form':form})

@require_http_methods(['GET', 'POST'])
@ratelimit(key='ip', rate='3/m', method='POST', block=True)
def token_validation_reset_password(request, uuid_user:str, token_reinitialisation:str):
    user = None
    try:
        user = User.objects.get(uuid=uuid_user)
    except User.DoesNotExist:
        pass
    if user is None :
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    
    is_valid = False
    reset_password_service = ResetPasswordService(user)
    try: 
        reset_password_service.verification_token(token_reinitialisation)
        is_valid = True
    except Exception as e:
        logger.error(f"token validation error : {e}")
        
    if not is_valid:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    
    
    if request.method == 'POST':
        form = UserPasswordForm(request.POST,instance=user)
        if form.is_valid():
            try:
                user = form.save()
                logger.info(f"User password modified{user.username}")
                ServerNotificationBuilder(request).set_message("Mot de passe modifié").set_statut("info").send()
                UserMail(user).send_password_changed_email()
                reset_password_service.clean()
                return redirect('login')
            except Exception as e:
                logger.error(e)
    if request.method == 'GET':
        form = UserPasswordForm(instance=user)
    return render(request, 'Html/Account/reset_password.html', {'form':form})