import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from main.domain.common.service.MusicService import MusicService
from main.domain.common.service.RandomizeTrackService import RandomizeTrackService
from main.domain.common.service.PlaylistService import PlaylistService
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from main.interface.ui.forms.private.PlaylistForm import PlaylistForm
from main.domain.common.service.DefaultColorPlaylistService import DefaultColorPlaylistService
from main.domain.common.enum.LinkMusicAllowedEnum import LinkMusicAllowedEnum
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.enum.ConfigTypeDataEnum import ConfigTypeDataEnum
from main.domain.private.formatter.TypePlaylistFormater import TypePlaylistFormater
from main.domain.common.service.SoundBoardService import SoundBoardService
from main.architecture.persistence.repository.MusicRepository import MusicRepository

from main.domain.common.utils.ExtractPaginator import extract_context_to_paginator
from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum
from main.domain.common.helper.ActivityContextHelper import ActivityContextHelper
from main.architecture.persistence.repository.SoundBoardRepository import SoundBoardRepository
from main.architecture.persistence.repository.PlaylistRepository import PlaylistRepository
from main.architecture.persistence.repository.TrackRepository import TrackRepository
from main.architecture.persistence.repository.PlaylistDuplicationHistoryRepository import PlaylistDuplicationHistoryRepository

from main.domain.common.service.PlaylistDuplicationService import PlaylistDuplicationService
from main.domain.common.exceptions.PlaylistDuplicationException import (
    PlaylistAlreadyDuplicatedException,
    PlaylistNotCopiableException
)



from main.domain.common.utils.logger import logger

@login_required
@require_http_methods(['GET'])
def playlist_read_copiable(request):
    playlist_type_filter = request.GET.get('playlistType', None)
    page_number = int(request.GET.get('page', 1))
  
    
    filter_search = {}
    if playlist_type_filter:
        try:
            type_playlist = PlaylistTypeEnum.searchEnumByValue(playlist_type_filter)
            filter_search['typePlaylist'] = type_playlist._name_
        except ValueError:
            playlist_type_filter = None
            
    queryset = PlaylistRepository().get_copiable_playlists_excluding_user(request.user, filter_search)
    paginator = Paginator(queryset, 50)
    context = extract_context_to_paginator(paginator, page_number)
    
    track_repository = TrackRepository()
    number_tracks_by_playlist = track_repository.get_number_tracks_by_playlist_queryset(queryset)
    
    context.update( {
        'number_tracks_by_playlist': number_tracks_by_playlist,
        'playlistType': PlaylistTypeEnum.convert_to_dict(),
        'selected_type': playlist_type_filter
    })
    
    return render(request, 'Html/Playlist/playlist_copiable.html', context)

@login_required
@require_http_methods(['GET'])
def playlist_copiable_preview(request):
    playlist_uuid = request.GET.get('playlistUuid', None)
    if(not playlist_uuid):
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    
    playlist = PlaylistRepository().get(playlist_uuid)
    if(not playlist or not playlist.is_copiable):
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    
    playlist.typePlaylistStr = PlaylistTypeEnum[playlist.typePlaylist].value
    list_track = TrackRepository().get_tracks_by_playlist(playlist)
    
    check_already_duplicated = PlaylistDuplicationHistoryRepository().find_existing_duplication(
        playlist.uuid,
        request.user
    )
    return render(request, 'Html/Playlist/playlist_copiable_preview.html', {'playlist': playlist, "list_track": list_track, "already_duplicated": check_already_duplicated is not None})


@login_required
@require_http_methods(['POST'])
def playlist_copiable_duplicate(request, playlist_uuid):
    if not playlist_uuid:
        return JsonResponse(
            {"error": ErrorMessageEnum.ELEMENT_NOT_FOUND, "message": "Playlist not found or not copiable 1"}, 
            status=404
        )
    
    # Récupérer la playlist source
    playlist = PlaylistRepository().get(playlist_uuid)
    if not playlist:
        return JsonResponse(
            {"error": "Playlist introuvable"}, 
            status=404
        )
        
    try:
        duplication_service = PlaylistDuplicationService(
            source_playlist=playlist,
            target_user=request.user
        )
        new_playlist = duplication_service.duplicate()
        
        return JsonResponse(
            {
                "success": True,
                "message": f"Playlist '{playlist.name}' dupliquée avec succès", 
                "new_playlist_uuid": str(new_playlist.uuid)
            }, 
            status=200
        )
    except PlaylistNotCopiableException as e:
        return JsonResponse(
            {
                "error": "Cette playlist n'est pas disponible à la duplication"
            }, 
            status=403
        )
    except PlaylistAlreadyDuplicatedException as e:
        return JsonResponse(
            {
                "error": f"Vous avez déjà dupliqué cette playlist le {e.duplicated_at}"
            }, 
            status=409
        )
    except Exception as e:
        logger.error(f"Erreur lors de la duplication de la playlist {playlist_uuid}: {str(e)}")
        return JsonResponse(
            {"error": "Une erreur inattendue est survenue lors de la duplication"}, 
            status=500
        )
    

    
