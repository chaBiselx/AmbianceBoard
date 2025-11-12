import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from main.domain.common.service.MusicService import MusicService
from main.domain.common.service.RandomizeTrackService import RandomizeTrackService
from main.domain.common.service.PlaylistService import PlaylistService
from main.domain.common.service.SharedSoundboardService import SharedSoundboardService
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from main.interface.ui.forms.private.PlaylistForm import PlaylistForm
from main.domain.common.service.DefaultColorPlaylistService import DefaultColorPlaylistService
from main.domain.common.enum.LinkMusicAllowedEnum import LinkMusicAllowedEnum
from main.domain.common.service.SoundBoardService import SoundBoardService
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum
from main.domain.common.helper.ActivityContextHelper import ActivityContextHelper
from main.architecture.persistence.repository.TrackRepository import TrackRepository
from main.domain.common.utils.cache.CacheFactory import CacheFactory


from main.domain.common.utils.logger import logger


@login_required
@require_http_methods(['GET'])
def playlist_show(request, soundboard_uuid):
    """Affichage d'un soundboard spécifique"""
    SharedSoundboardService(request, soundboard_uuid).reset_soundboard_player()
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    
    if not soundboard:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    else:
        activity = ActivityContextHelper.set_action(request, activity_type=UserActivityTypeEnum.SOUNDBOARD_VIEW, user=request.user, content_object=soundboard)
        return render(request, 'Html/Soundboard/soundboard_read.html', {
            'soundboard': soundboard, 
            'PlaylistTypeEnum': list(PlaylistTypeEnum),
            'trace_user_activity': activity
        })

@login_required
@require_http_methods(['GET'])
def music_stream(request, soundboard_uuid, playlist_uuid) -> HttpResponse|JsonResponse:
    """Stream d'une musique aléatoire d'une playlist via soundboard"""
    cache = CacheFactory.get_default_cache()
    cache_key = f"musicStream:{request.session.session_key}:{soundboard_uuid}:{playlist_uuid}:{request.GET.get('i','0')}"
    
    try:
        if request.headers.get('X-Metadata-Only') == 'true':
            track_id = cache.get(cache_key)
            if track_id :
                track = TrackRepository().get(track_id, playlist_uuid)
                if track:
                    ret = JsonResponse({"duration":  track.get_duration()}, status=200)
        else:
            track = (RandomizeTrackService(request)).generate_private(playlist_uuid)
            if track:
                # Utilisation du service de soundboard partagé pour gérer le stream
                SharedSoundboardService(request, soundboard_uuid).music_start(playlist_uuid, track)
                cache.set(cache_key, track.id, timeout=60)
                ret = track.get_reponse_content()
        if ret:
            return ret
    except Exception as e:
        logger.error(f"Error in public_music_stream: {e}")
    return HttpResponse(ErrorMessageEnum.ELEMENT_NOT_FOUND.value, status=404)
    

    try:
        if request.method == 'HEAD':
            ret = HttpResponse()
            ret ['Content-Duration'] = track.get_duration()
        else:
            # Utilisation du service de soundboard partagé pour gérer le stream
            SharedSoundboardService(request, soundboard_uuid).music_start(playlist_uuid, track)
            ret = track.get_reponse_content()
        if ret:
            return ret
    except Exception as e:
        logger.error(f"Error in music_stream: {e}")
    return HttpResponse(ErrorMessageEnum.ELEMENT_NOT_FOUND.value, status=404)


@login_required
@require_http_methods(['POST'])
def update_direct_volume(request, playlist_uuid) -> JsonResponse:
    """Mise à jour du volume d'une playlist"""
    if request.method == 'POST':
        playlist = (PlaylistService(request)).get_playlist(playlist_uuid)
        if not playlist:
            return JsonResponse({"error": ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
        else:
            data = json.loads(request.body)
            volume = data.get('volume')
            if volume is not None:
                playlist.volume = volume
                playlist.save()
                return JsonResponse({"message": "volume updated"}, status=200)
        
    return JsonResponse({"error": ErrorMessageEnum.METHOD_NOT_SUPPORTED.value}, status=405)

