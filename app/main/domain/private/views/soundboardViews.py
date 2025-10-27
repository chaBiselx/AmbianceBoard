import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from main.domain.common.utils.settings import Settings
from main.domain.private.manager.SoundBoardPlaylistManager import SoundBoardPlaylistManager
from main.service.SoundBoardService import SoundBoardService
from main.domain.common.service.PlaylistService import PlaylistService
from main.service.SoundboardPlaylistService import SoundboardPlaylistService
from main.domain.private.form.SoundBoardForm import SoundBoardForm
from main.architecture.persistence.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository
from main.architecture.persistence.repository.SoundBoardRepository import SoundBoardRepository
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.enum.ConfigTypeDataEnum import ConfigTypeDataEnum
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from django.core import exceptions
from main.domain.common.utils.logger import logger


@login_required
@require_http_methods(['GET'])
def soundboard_list(request):
    """Liste tous les soundboards de l'utilisateur connecté"""
    try:
        soundboards = SoundBoardRepository().get_list_from_user(request.user)
    except Exception:
        soundboards = []
    
    return render(request, 'Html/Soundboard/soundboard_list.html', {'soundboards': soundboards})




@login_required
@require_http_methods(['GET'])
def soundboard_organize(request, soundboard_uuid):
    """Organisation des playlists dans un soundboard"""
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if not soundboard:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    
    soundboard_manager = SoundBoardPlaylistManager(request, soundboard)

    max_sections = SoundboardPlaylistRepository().get_max_section(soundboard)
    return render(request, 'Html/Soundboard/soundboard_organize.html', {
        'limite_max_section' : Settings.get('SOUNDBOARD_LIMIT_SECTION'),
        'soundboard': soundboard, 
        'actualPlaylist': soundboard_manager.get_playlists, 
        'unassociatedPlaylists': soundboard_manager.get_unassociated_playlists,
        'max_sections': range(1, max_sections + 1)
    })


@login_required
@require_http_methods(['POST', 'DELETE', 'UPDATE'])
def soundboard_organize_update(request, soundboard_uuid):
    """Mise à jour de l'organisation des playlists dans un soundboard"""
    try:
        soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
        data = json.loads(request.body.decode('utf-8'))
        playlist = (PlaylistService(request)).get_playlist(data['idPlaylist'])
        new_order = None
        
        if 'newOrder' in data.keys():
            if data['newOrder'] is None:
                new_order = 1
            else:
                new_order = int(data['newOrder'])
        section = 1  # Valeur par défaut
        if 'section' in data.keys():
            section = int(data['section'])
            
        soundboard_playlist_service = SoundboardPlaylistService(soundboard)
        if not playlist:
            raise exceptions.ObjectDoesNotExist
        if request.method == 'POST':
            soundboard_playlist_service.add(playlist, new_order, section)
            return JsonResponse({'success': 'playlist added', 'order': playlist.get_order()}, status=200)
        if request.method == 'UPDATE':
            soundboard_playlist_service.update(playlist, new_order, section)
            return JsonResponse({'success': 'playslist added', 'order': playlist.get_order()}, status=200)
        if request.method == 'DELETE':
            soundboard_playlist_service.remove(playlist)
            return JsonResponse({'success': 'playslist deleted'}, status=200)
    except Exception as e:
        logger.error(f"soundboard_organize_update : {e}")
        return JsonResponse({"error": "playslist non trouvé."}, status=404)
