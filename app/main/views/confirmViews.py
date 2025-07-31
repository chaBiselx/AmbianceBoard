import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login,logout, authenticate
from django.contrib.auth.models import Group
from main.models.User import User
from main.enum.GroupEnum import GroupEnum
from django.http import JsonResponse
from main.utils.logger import logger
from main.forms.CreateUserForm import CreateUserForm
from main.email.UserMail import UserMail
from main.service.FailedLoginAttemptService import FailedLoginAttemptService
from django.core.exceptions import ValidationError
from main.service.ConfirmationUserService import ConfirmationUserService
from main.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum


@login_required
@require_http_methods(['GET'])
def confirm_account(request, uuid_user:str, confirmation_token:str):
    logger.info("Starting ConfirmAccount View")
    try:
        user = User.objects.get(uuid=uuid_user)
        ConfirmationUserService(user).verification_token(confirmation_token)
        
       

        return redirect('login')
    except Exception as e:
        logger.error(e)
        return render(request,  HtmlDefaultPageEnum.ERROR_404.value, status=404)
    