import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from ...service.MediaAudioService import MediaAudioService



@login_required #TODO add permission 
def clean_media_folder(request) -> JsonResponse:
    try:
        logger = logging.getLogger(__name__)
        logger.warning("Starting ClearMediaFolderCron")
        (MediaAudioService()).clear_media_audio()
        logger.warning("Ending ClearMediaFolderCron")
        return JsonResponse({"message": "OK"}, status=200)
    except Exception:
        return JsonResponse({"error": "Unexpected error"}, status=500)
    
