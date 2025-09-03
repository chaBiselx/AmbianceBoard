import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from main.architecture.persistence.models.User import User
from main.domain.common.repository.UserRepository import UserRepository
from main.domain.common.utils.logger import logger
from main.domain.common.service.ConfirmationUserService import ConfirmationUserService
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.domain.common.utils.ServerNotificationBuilder import ServerNotificationBuilder


@require_http_methods(['GET'])
def confirm_account(request, uuid_user:str, confirmation_token:str):
    logger.info("Starting ConfirmAccount View")
    user = UserRepository().get_user(uuid_user)
    if user:
        confirmed = ConfirmationUserService(user).verification_token(confirmation_token)
        if confirmed:
            ServerNotificationBuilder(request).set_message(
                "Votre compte a été validé."
                ).set_statut("info").send()
            
        return redirect('login')
    else:
        logger.error("confirm_account User not found")
        return render(request,  HtmlDefaultPageEnum.ERROR_404.value, status=404)
    