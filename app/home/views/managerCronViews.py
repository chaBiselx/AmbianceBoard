import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from home.service.MediaAudioService import MediaAudioService
from home.service.MediaImgPlaylistService import MediaImgPlaylistService
from home.service.MediaImgSoundboardService import MediaImgSoundboardService
from home.enum.PermissionEnum import PermissionEnum
from home.enum.ErrorMessageEnum import ErrorMessageEnum
from home.service.cron.UserTierExpirationService import UserTierExpirationService
from home.service.cron.DomainBlacklistCronService import DomainBlacklistCronService
    

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def clean_media_folder(request) -> JsonResponse:
    try:
        logger = logging.getLogger('home')
        logger.warning("Starting ClearMediaFolder View")
        (MediaAudioService()).clear_media_audio()
        (MediaImgPlaylistService()).clear_media_img()
        (MediaImgSoundboardService()).clear_media_img()
        
        logger.warning("Ending ClearMediaFolder View")
        return JsonResponse({"message": "OK"}, status=200)
    except Exception as e:
        return JsonResponse({"error": ErrorMessageEnum.INTERNAL_SERVER_ERROR.value, "message": str(e)}, status=500)
    
@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def expire_account(request) -> JsonResponse:
    try:
        logger = logging.getLogger('home')
        logger.warning("Starting ExpireAccount View")
        user_tier_expiration_service = UserTierExpirationService()
        user_tier_expiration_service.handle_expired_tiers()
        user_tier_expiration_service.send_expiration_warnings()
        
        logger.warning("Ending ExpireAccount View")
        return JsonResponse({"message": "OK"}, status=200)
    except Exception as e:
        return JsonResponse({"error": ErrorMessageEnum.INTERNAL_SERVER_ERROR.value, "message": str(e)}, status=500)
    

    
@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def sync_domain_blacklist(request) -> JsonResponse:
    try:
        logger = logging.getLogger('home')
        logger.warning("Starting SyncDomainBlacklist View")
        domain_blacklist_cron_service = DomainBlacklistCronService()
        domain_blacklist_cron_service.sync_blacklist()
        logger.warning("Ending SyncDomainBlacklist View")
        return JsonResponse({"message": "OK"}, status=200)
    except Exception as e:
        return JsonResponse({"error": ErrorMessageEnum.INTERNAL_SERVER_ERROR.value, "message": str(e)}, status=500)
    
