import logging
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from home.service.MusicService import MusicService
from home.service.RandomizeTrackService import RandomizeTrackService
from home.service.PlaylistService import PlaylistService
from home.service.SharedSoundboardService import SharedSoundboardService
from home.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from home.enum.ErrorMessageEnum import ErrorMessageEnum
from home.forms.PlaylistForm import PlaylistForm
from home.service.DefaultColorPlaylistService import DefaultColorPlaylistService
from home.enum.LinkMusicAllowedEnum import LinkMusicAllowedEnum
from home.service.SoundBoardService import SoundBoardService
from home.enum.PlaylistTypeEnum import PlaylistTypeEnum



logger = logging.getLogger('home')


@login_required
@require_http_methods(['GET'])
def playlist_show(request, soundboard_uuid):
    """Affichage d'un soundboard spécifique"""
    SharedSoundboardService(request, soundboard_uuid).music_stop_all()
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    
    if not soundboard:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    else:
        return render(request, 'Html/Soundboard/soundboard_read.html', {
            'soundboard': soundboard, 
            'PlaylistTypeEnum': list(PlaylistTypeEnum)
        })

@login_required
@require_http_methods(['GET'])
def music_stream(request, soundboard_uuid, playlist_uuid) -> HttpResponse:
    """Stream d'une musique aléatoire d'une playlist via soundboard"""
    track = (RandomizeTrackService(request)).generate_private(playlist_uuid)
    if not track:
        return HttpResponse(ErrorMessageEnum.ELEMENT_NOT_FOUND.value, status=404)
    
    SharedSoundboardService(request, soundboard_uuid).music_start(playlist_uuid, track)

    try:
        response = track.get_reponse_content()
        if response:
            return response
    except Exception as e:
        logger.error(f"Error in music_stream: {e}")
    return HttpResponse(ErrorMessageEnum.INTERNAL_SERVER_ERROR.value, status=500)


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

