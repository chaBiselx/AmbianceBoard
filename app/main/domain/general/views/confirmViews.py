import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from main.architecture.persistence.models.User import User
from main.domain.common.utils.logger import logger
from main.domain.common.service.ConfirmationUserService import ConfirmationUserService
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum


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
    