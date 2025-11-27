from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from main.domain.cron.service.MediaAudioService import MediaAudioService
from main.domain.cron.service.MediaImgPlaylistService import MediaImgPlaylistService
from main.domain.cron.service.MediaImgSoundboardService import MediaImgSoundboardService
from main.domain.cron.service.UserTierExpirationService  import UserTierExpirationService
from main.domain.cron.service.DomainBlacklistCronService import DomainBlacklistCronService
from main.domain.cron.service.SharedSoundboardService import SharedSoundboardService
from main.domain.cron.service.PurgeUserActivityService import PurgeUserActivityService
from main.domain.common.utils.logger import logger
from main.architecture.persistence.repository.GeneralNotificationRepository import GeneralNotificationRepository
from main.interface.ui.forms.manager.GeneralNotificationForm import GeneralNotificationForm
from django.core.paginator import Paginator
from main.domain.common.utils.ExtractPaginator import extract_context_to_paginator


@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def listing_notifications(request):
    page_number = int(request.GET.get('page', 1))

    queryset = GeneralNotificationRepository().get_all_notifications()
    paginator = Paginator(queryset, 50)
    context = extract_context_to_paginator(paginator, page_number)
    context.update({'title': 'Liste des notifications'})
  
    return render(request, 'Html/Manager/notification_listing.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def manage_notification(request, uuid=None):
    """Créer ou modifier une notification selon la présence de l'UUID."""
    notification = None
    is_update = uuid is not None
    
    if is_update:
        notification = GeneralNotificationRepository().get_notification_by_uuid(uuid)
        if notification is None:
            messages.error(request, 'Notification introuvable.')
            return redirect('managerNotifications')
    
    if request.method == 'POST':
        form = GeneralNotificationForm(request.POST, instance=notification)
        if form.is_valid():
            notification = form.save()
            action_msg = 'modifiée' if is_update else 'créée'
            messages.success(request, f'Notification {action_msg} avec succès.')
            logger.info(f"Notification {action_msg}: {notification.uuid} par {request.user.username}")
            return redirect('managerNotifications')
    else:
        form = GeneralNotificationForm(instance=notification)
    
    context = {
        'title': 'Modifier une notification' if is_update else 'Créer une notification',
        'form': form,
        'notification': notification,
        'action': 'update' if is_update else 'create'
    }
    return render(request, 'Html/Manager/notification_form.html', context)

