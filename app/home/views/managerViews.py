import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from home.service.MediaAudioService import MediaAudioService
from home.service.MediaImgPlaylistService import MediaImgPlaylistService
from home.service.MediaImgSoundboardService import MediaImgSoundboardService
from home.enum.PermissionEnum import PermissionEnum


@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def manager_dashboard(request) -> HttpResponse:
    return render(request, 'Html/Manager/dashboard.html')
    

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
        return JsonResponse({"error": "Unexpected error", "message": str(e)}, status=500)
    

