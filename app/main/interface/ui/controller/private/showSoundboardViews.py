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
from main.domain.common.service.SoundboardPlaylistService import SoundboardPlaylistService
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.factory.UserParametersFactory import UserParametersFactory
from main.domain.common.service.SoundboardPlaylistRenderService import SoundboardPlaylistRenderService
from main.architecture.persistence.models.Playlist import Playlist

from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum
from main.domain.common.helper.ActivityContextHelper import ActivityContextHelper
from main.domain.common.helper.WebSocketInitializationHelper import WebSocketInitializationHelper
from main.architecture.persistence.repository.TrackRepository import TrackRepository
from main.architecture.persistence.repository.PlaylistRepository import PlaylistRepository
from main.domain.common.utils.cache.CacheFactory import CacheFactory
from main.architecture.persistence.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository
from main.architecture.persistence.repository.PlaylistDuplicationHistoryRepository import PlaylistDuplicationHistoryRepository
from main.domain.common.service.PlaylistDuplicationService import PlaylistDuplicationService
from main.domain.common.exceptions.PlaylistDuplicationException import (
    PlaylistAlreadyDuplicatedException,
    PlaylistNotCopiableException
)


from django.core.paginator import Paginator
from main.domain.common.utils.ExtractPaginator import extract_context_to_paginator
from main.domain.common.utils.logger import logger
from django.urls import reverse


@login_required
@require_http_methods(['GET'])
def playlist_show(request, soundboard_uuid):
    """Affichage d'un soundboard spécifique"""
    SharedSoundboardService(request, soundboard_uuid).reset_soundboard_player()
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    
    if not soundboard:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    else:
        soundboard_playlist_repository = SoundboardPlaylistRepository()
        
        activity = ActivityContextHelper.set_action(request, activity_type=UserActivityTypeEnum.SOUNDBOARD_VIEW, user=request.user, content_object=soundboard)
        
        response = render(request, 'Html/Soundboard/soundboard_read.html', {
            'soundboard': soundboard, 
            'PlaylistTypeMixer': DefaultColorPlaylistService(request.user).get_list_playlist_enum_with_color(),
            'trace_user_activity': activity,
            'list_shortcut_keyboard': soundboard_playlist_repository.get_list_shortcut_keyboard(soundboard),
            'link_music_allowed': LinkMusicAllowedEnum.convert_to_dict(),
        })
        
        # Auto-initialisation WebSocket
        return WebSocketInitializationHelper.setup_websocket_board_cookies(response, request, soundboard_uuid)

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
            track = (RandomizeTrackService(request)).generate_private(soundboard_uuid, playlist_uuid)
            if track:
                # Utilisation du service de soundboard partagé pour gérer le stream
                SharedSoundboardService(request, soundboard_uuid).music_start(playlist_uuid, track)
                cache.set(cache_key, track.id, timeout=60)
                ret = track.get_reponse_content()
        if ret:
            return ret
    except Exception as e:
        logger.error(f"Error in soundboard_music_stream: {e}")
    return HttpResponse(ErrorMessageEnum.ELEMENT_NOT_FOUND.value, status=404)



@login_required
@require_http_methods(['GET'])
def playlist_tracks_list(request, soundboard_uuid) -> JsonResponse:
    """Liste des tracks de toutes les playlists d'un soundboard en JSON"""
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if not soundboard:
        return JsonResponse({"error": ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

    track_repository = TrackRepository()
    result = {}
    for _section, playlists in soundboard.get_list_playlist_ordered():
        for playlist in playlists:
            tracks = track_repository.get_tracks_by_playlist(playlist)
            result[str(playlist.uuid)] = [
                {
                    "id": track.id,
                    "name": track.get_name(),
                    "duration": track.get_duration(),
                    "uri": reverse('privateSpecificTrackStream', args=[soundboard_uuid, playlist.uuid, track.id]),
                }
                for track in tracks
            ]

    return JsonResponse(result, status=200)

@login_required
@require_http_methods(['GET'])
def private_specific_track_stream(request, soundboard_uuid, playlist_uuid, music_id) ->  HttpResponse|JsonResponse:
    cache = CacheFactory.get_default_cache()
    cache_key = f"musicStream:{request.session.session_key}:{soundboard_uuid}:{playlist_uuid}:{music_id}:{request.GET.get('i','0')}"
    ret = None
    try:
        if request.headers.get('X-Metadata-Only') == 'true':
            track_id = cache.get(cache_key)
            if track_id :
                track = TrackRepository().get(track_id, playlist_uuid)
                if track:
                    ret = JsonResponse({"duration":  track.get_duration()}, status=200)
        else:
            track = (RandomizeTrackService(request)).get_specific_private(soundboard_uuid, playlist_uuid, music_id)
            if track:
                # Utilisation du service de soundboard partagé pour gérer le stream
                SharedSoundboardService(request, soundboard_uuid).music_start(playlist_uuid, track)
                cache.set(cache_key, track.id, timeout=60)
                ret = track.get_reponse_content()
        if ret:
            return ret
    except Exception as e:
        logger.error(f"Error in private_specific_track_stream: {e}")
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


@login_required
@require_http_methods(['GET'])
def soundboard_edit_mode_panel(request, soundboard_uuid):
    """Retourne la vue partielle pour le mode édition du soundboard."""
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if not soundboard:
        return render(request, HtmlDefaultPageEnum.ERROR_404_MODAL.value, status=404, modal=True)

    return render(request, 'Html/Soundboard/modal/soundboard_edit_mode_panel.html', {
        'soundboard': soundboard,
        'playlistType': PlaylistTypeEnum.convert_to_dict(),
    })


@login_required
@require_http_methods(['GET'])
def soundboard_edit_mode_playlist_list(request, soundboard_uuid):
    """Retourne la liste paginée des playlists copiables pour le mode édition."""
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if not soundboard:
        return HttpResponse(status=404)

    playlist_type_filter = request.GET.get('playlistType', None)
    filter_search = {}
    if playlist_type_filter:
        try:
            type_playlist = PlaylistTypeEnum.searchEnumByValue(playlist_type_filter)
            filter_search['typePlaylist'] = type_playlist._name_
        except ValueError:
            playlist_type_filter = None

    playlists = PlaylistRepository().get_copiable_playlists_for_soundboard(request.user, filter_search)
    try:
        page_number = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_number = 1

    paginator = Paginator(playlists, 10)
    context = extract_context_to_paginator(paginator, page_number)

    return render(request, 'Html/Soundboard/modal/soundboard_edit_mode_playlist_list.html', {
        'soundboard': soundboard,
        'page_objects': context['page_objects'],
        'paginator': context['paginator'],
    })


@login_required
@require_http_methods(['POST'])
def soundboard_edit_mode_duplicate_playlist(request, soundboard_uuid, playlist_uuid) -> JsonResponse:
    """Duplique une playlist publique et l'ajoute directement au soundboard cible."""
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if not soundboard:
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

    playlist = PlaylistRepository().get(playlist_uuid)
    if not playlist:
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

    if not playlist.is_copiable or playlist.moderator_ban_copie:
        return JsonResponse({'error': "Cette playlist n'est pas disponible à la duplication"}, status=403)

    existing = PlaylistDuplicationHistoryRepository().find_existing_duplication_in_soundboard(
        source_playlist_uuid=playlist.uuid,
        target_user=request.user,
        target_soundboard=soundboard
    )
    if existing:
        return JsonResponse({'error': ErrorMessageEnum.PLAYLIST_ALREADY_EXISTS_IN_SOUNDBOARD.value}, status=409)

    try:
        render_service = SoundboardPlaylistRenderService(request)
        duplication_service = PlaylistDuplicationService(
            source_playlist=playlist,
            target_user=request.user
        )
        duplicated_playlist = duplication_service.duplicate()

        SoundboardPlaylistService(soundboard).add_default(duplicated_playlist)

        playlist_html = render_service.render_playlist_item(duplicated_playlist, soundboard)

        response_payload = {
            'success': True,
            'message': "Playlist ajoutée en mode édition",
            'playlist_uuid': str(duplicated_playlist.uuid),
            'playlist_html': playlist_html,
        }

        return JsonResponse(response_payload, status=200)
    except PlaylistNotCopiableException:
        return JsonResponse({'error': "Cette playlist n'est pas disponible à la duplication"}, status=403)
    except PlaylistAlreadyDuplicatedException:
        return JsonResponse({'error': ErrorMessageEnum.PLAYLIST_ALREADY_EXISTS_IN_SOUNDBOARD.value}, status=409)
    except Exception as e:
        logger.error(f"Erreur duplication mode édition pour soundboard {soundboard_uuid}: {e}")
        return JsonResponse({'error': ErrorMessageEnum.INTERNAL_SERVER_ERROR.value}, status=500)


@login_required
@require_http_methods(['POST'])
def soundboard_edit_mode_create_playlist(request, soundboard_uuid) -> JsonResponse:
    """Crée une playlist depuis la modal mode édition et l'ajoute au soundboard cible."""
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if not soundboard:
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

    playlist_name = (request.POST.get('name') or '').strip()
    playlist_type = request.POST.get('typePlaylist')

    if not playlist_name:
        return JsonResponse({'error': "Le nom de la playlist est obligatoire"}, status=400)

    valid_playlist_types = dict(Playlist.typePlaylist.field.choices)
    if not playlist_type or playlist_type not in valid_playlist_types:
        return JsonResponse({'error': "Type de playlist invalide"}, status=400)

    user_parameters = UserParametersFactory(request.user)
    if PlaylistRepository().count_private(request.user) >= user_parameters.limit_playlist:
        return JsonResponse({
            'error': f"Vous avez atteint la limite de playlist total ({user_parameters.limit_playlist})."
        }, status=403)

    try:
        render_service = SoundboardPlaylistRenderService(request)
        playlist = Playlist(
            user=request.user,
            name=playlist_name,
            typePlaylist=playlist_type,
        )
        playlist.save()
        SoundboardPlaylistService(soundboard).add_default(playlist)

        playlist_html = render_service.render_playlist_item(playlist, soundboard)

        return JsonResponse({
            'success': True,
            'message': "Playlist créée et ajoutée au soundboard",
            'playlist_uuid': str(playlist.uuid),
            'playlist_html': playlist_html,
            'add_music_url': reverse('add_music_from_soundboard', args=[playlist.uuid]),
        }, status=201)
    except Exception as e:
        logger.error("===================================================")
        logger.error(f"Erreur création mode édition pour soundboard {soundboard_uuid}: {e}")
        return JsonResponse({'error': "Une erreur inattendue est survenue"}, status=500)


@login_required
@require_http_methods(['GET'])
def soundboard_edit_mode_my_playlist_list(request, soundboard_uuid):
    """Retourne la liste paginée des playlists de l'utilisateur non encore intégrées dans le soundboard."""
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if not soundboard:
        return HttpResponse(status=404)

    playlist_type_filter = request.GET.get('playlistType', None)
    filter_search = {}
    if playlist_type_filter:
        try:
            type_playlist = PlaylistTypeEnum.searchEnumByValue(playlist_type_filter)
            filter_search['typePlaylist'] = type_playlist._name_
        except ValueError:
            playlist_type_filter = None

    playlists = PlaylistRepository().get_user_playlists_not_in_soundboard(request.user, soundboard, filter_search)
    try:
        page_number = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_number = 1

    paginator = Paginator(playlists, 10)
    context = extract_context_to_paginator(paginator, page_number)

    return render(request, 'Html/Soundboard/modal/soundboard_edit_mode_my_playlist_list.html', {
        'soundboard': soundboard,
        'page_objects': context['page_objects'],
        'paginator': context['paginator'],
    })


@login_required
@require_http_methods(['POST'])
def soundboard_edit_mode_add_my_playlist(request, soundboard_uuid, playlist_uuid) -> JsonResponse:
    """Ajoute une playlist existante de l'utilisateur dans le soundboard cible."""
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if not soundboard:
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

    playlist = PlaylistRepository().get(playlist_uuid)
    if not playlist:
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

    if playlist.user != request.user:
        return JsonResponse({'error': "Vous n'êtes pas propriétaire de cette playlist"}, status=403)

    existing = SoundboardPlaylistRepository().get(soundboard, playlist)
    if existing:
        return JsonResponse({'error': ErrorMessageEnum.PLAYLIST_ALREADY_EXISTS_IN_SOUNDBOARD.value}, status=409)

    try:
        render_service = SoundboardPlaylistRenderService(request)
        SoundboardPlaylistService(soundboard).add_default(playlist)

        playlist_html = render_service.render_playlist_item(playlist, soundboard)

        return JsonResponse({
            'success': True,
            'message': "Playlist ajoutée au soundboard",
            'playlist_uuid': str(playlist.uuid),
            'playlist_html': playlist_html,
        }, status=200)
    except Exception as e:
        logger.error(f"Erreur ajout playlist mode édition pour soundboard {soundboard_uuid}: {e}")
        return JsonResponse({'error': ErrorMessageEnum.INTERNAL_SERVER_ERROR.value}, status=500)

