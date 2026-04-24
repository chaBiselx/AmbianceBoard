import random
import json
import base64
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from main.domain.common.service.SoundBoardService import SoundBoardService
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.architecture.persistence.repository.SoundBoardRepository import SoundBoardRepository
from main.architecture.persistence.repository.SharedSoundboardRepository import SharedSoundboardRepository
from main.architecture.persistence.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository
from django.contrib.sites.shortcuts import get_current_site
from main.domain.common.utils.url import get_full_url, get_full_ws
from main.domain.common.service.RandomizeTrackService import RandomizeTrackService
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from main.domain.common.utils.settings import Settings
from main.domain.common.utils.logger import logger
from main.domain.common.service.DefaultColorPlaylistService import DefaultColorPlaylistService


from main.architecture.persistence.repository.TrackRepository import TrackRepository
from main.domain.common.utils.cache.CacheFactory import CacheFactory

from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum
from main.domain.common.helper.ActivityContextHelper import ActivityContextHelper

@require_http_methods(['GET'])
def publish_soundboard(request, soundboard_uuid):
    """Affiche l'URL publique pour un soundboard donné (réutilise la session WebSocket existante)"""
    soundboard = SoundBoardRepository().get(soundboard_uuid)
    if not soundboard:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)

    # Réutiliser la session existante au lieu d'en créer une nouvelle
    shared = SharedSoundboardRepository().get_or_create_for_owner(soundboard=soundboard)
    
    ActivityContextHelper.set_action(request, activity_type=UserActivityTypeEnum.SOUNDBOARD_SHARE, user=request.user)
    return render(request, 'Html/Shared/publich_soundboard.html', {'shared_url': get_full_url(reverse('shared_soundboard', args=[soundboard_uuid, shared.token]))})



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
        ws_url = get_full_ws(f'{request.get_host()}{ws_path}')
        return render(request, 'Html/Shared/soundboard_read.html', {'soundboard': soundboard, 'token' : token, 'PlaylistTypeMixer': DefaultColorPlaylistService(request.user).get_list_playlist_enum_with_color(), 'ws_url' : ws_url, 'list_shortcut_keyboard': []})
    
@require_http_methods(['GET'])
def shared_soundboard_refresh(request, soundboard_uuid, token):
    soundboard = (SoundBoardService(request)).get_soundboard_from_shared_soundboard(soundboard_uuid, token)
    if not soundboard :
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    else:   
        return render(request, 'Html/partial/soundboard/board.html', {'soundboard': soundboard,  'master': False, 'owner': False})


@require_http_methods(['GET'])
def shared_music_stream(request, soundboard_uuid, playlist_uuid, token, music_id) ->  HttpResponse|JsonResponse:
    cache = CacheFactory.get_default_cache()
    cache_key = f"musicStream:{request.session.session_key}:{soundboard_uuid}:{playlist_uuid}:specific:{music_id}"
    
    try:
        if request.headers.get('X-Metadata-Only') == 'true':
            track_id = cache.get(cache_key)
            
            if track_id :
                track = TrackRepository().get(track_id, playlist_uuid)
                if track:
                    ret = JsonResponse({"duration":  track.get_duration()}, status=200)
        else:
            track = (RandomizeTrackService(request)).get_shared(soundboard_uuid, playlist_uuid, token, music_id )
            if track:
                cache.set(cache_key, track.id, timeout=60)
                ret = track.get_reponse_content()
        if ret:
            return ret
    except Exception as e:
        logger.error(f"Error in shared_music_stream: {e}")
    return HttpResponse(ErrorMessageEnum.ELEMENT_NOT_FOUND.value, status=404)
