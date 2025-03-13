import uuid
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


def confirm_account(request, uuid_user:str, confirmation_token:str):
    logger = logging.getLogger('home')
    logger.info("Starting ConfirmAccount View")
    try:
        user = User.objects.get(uuid=uuid_user)
        ConfirmationUserService(user).verification_token(confirmation_token)
        
       

        return redirect('login')
    except Exception as e:
        logger.error(e)
        return render(request,  'Html/General/404.html', status=404)
    