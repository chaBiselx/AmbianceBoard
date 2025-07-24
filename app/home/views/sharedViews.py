import random
import json
import base64
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from home.service.SoundBoardService import SoundBoardService #
from home.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum #
from home.enum.PlaylistTypeEnum import PlaylistTypeEnum
from home.models.SharedSoundboard import SharedSoundboard
from home.models.SoundBoard import SoundBoard
from django.contrib.sites.shortcuts import get_current_site
from home.utils.url import get_full_url
from home.service.RandomizeTrackService import RandomizeTrackService
from home.service.SharedSoundboardService import SharedSoundboardService
from home.enum.ErrorMessageEnum import ErrorMessageEnum





@require_http_methods(['GET'])
def publish_soundboard(request, soundboard_uuid):
    
    shared = SharedSoundboard.objects.create(soundboard=SoundBoard.objects.get(uuid=soundboard_uuid))
    shared.save()
    
    response = render (request, 'Html/Shared/publich_soundboard.html', {'shared_url' :  get_full_url(reverse('shared_soundboard', args=[soundboard_uuid, shared.token]))})
    
    ws_path = reverse('soundboard_ws', kwargs={
        'soundboard_uuid': soundboard_uuid,
        'token': shared.token,
    })
    ws_url = f'ws://{request.get_host()}{ws_path}'
    response.set_cookie(
                            'WebSocketToken', 
                            shared.token, 
                            max_age=3600*10*24,
                            httponly=False,
                            secure=True,    # HTTPS uniquement
                            samesite='Strict'  # Protection contre les attaques CSRF
                        )
    response.set_cookie(
                            'WebSocketUrl', 
                            base64.urlsafe_b64encode(ws_url.encode('utf-8')).decode('utf-8'),
                            max_age=3600*10*24,
                            httponly=False,
                            secure=True,    # HTTPS uniquement
                            samesite='Strict'  # Protection contre les attaques CSRF
                        )
    return response

    
    


@require_http_methods(['GET'])
def shared_soundboard_read(request, soundboard_uuid, token):
    soundboard = (SoundBoardService(request)).get_soundboard_from_shared_soundboard(soundboard_uuid, token)
    if not soundboard :
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    else:   
        ws_path = reverse('soundboard_ws', kwargs={
            'soundboard_uuid': soundboard.uuid,
            'token': token,
        })
        ws_url = f'ws://{request.get_host()}{ws_path}'
        return render(request, 'Html/Shared/soundboard_read.html', {'soundboard': soundboard, 'PlaylistTypeEnum' : list(PlaylistTypeEnum) , 'ws_url' : ws_url})


@require_http_methods(['GET'])
def shared_music_stream(request, soundboard_uuid, playlist_uuid, token, music_id) -> HttpResponse:
 
    track = (RandomizeTrackService(request)).get_shared(soundboard_uuid, playlist_uuid, token, music_id)
    if not track :
        return HttpResponse("Musique introuvable.", status=404)
    
    try:
        response = track.get_reponse_content()
        if response:
            return response
    except Exception as e:
        logging.error(f"Error in music_stream: {e}")
    return HttpResponse(ErrorMessageEnum.INTERNAL_SERVER_ERROR.value, status=500)
