from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from main.domain.common.service.SoundBoardService import SoundBoardService
from main.domain.common.service.PlaylistProposalService import PlaylistProposalService
from main.domain.common.service.RandomizeTrackService import RandomizeTrackService
from main.domain.common.service.SharedSoundboardService import SharedSoundboardService
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from main.architecture.persistence.repository.PlaylistRepository import PlaylistRepository
from main.architecture.persistence.repository.PlaylistTagRepository import PlaylistTagRepository
from main.architecture.persistence.repository.PlaylistProposalRepository import PlaylistProposalRepository
from main.domain.common.exceptions.PlaylistProposalException import (
    PlaylistProposalAlreadyExistsException,
    PlaylistProposalNotEligibleException,
    PlaylistProposalUnauthorizedException,
    PlaylistProposalInvalidStatusException,
)
from main.domain.common.utils.ExtractPaginator import extract_context_to_paginator
from main.domain.common.utils.cache.CacheFactory import CacheFactory
from main.architecture.persistence.repository.TrackRepository import TrackRepository
from main.domain.common.utils.logger import logger


@require_http_methods(['GET'])
def public_soundboard_propose_my_playlist_list(request, soundboard_uuid):
    """Retourne la liste paginée des playlists de l'utilisateur proposables à ce soundboard public."""
    if not request.user.is_authenticated:
        return render(request, 'Html/Soundboard/modal/soundboard_propose_playlist_need_connexion.html', {'soundboard_uuid': soundboard_uuid})

    soundboard = (SoundBoardService(request)).get_public_soundboard(soundboard_uuid)
    if not soundboard or soundboard.user == request.user:
        return HttpResponse(status=404)

    playlist_type_filter = request.GET.get('playlistType', None)
    playlist_tag_filter = request.GET.get('playlistTag', None)
    filter_search = {}
    if playlist_type_filter:
        try:
            type_playlist = PlaylistTypeEnum.searchEnumByValue(playlist_type_filter)
            filter_search['typePlaylist'] = type_playlist._name_
        except ValueError:
            playlist_type_filter = None

    if playlist_tag_filter:
        normalized_label = str(playlist_tag_filter).strip().lower().replace(' ', '-')
        if normalized_label:
            filter_search['playlistTagLabel'] = normalized_label
            playlist_tag_filter = normalized_label
        else:
            playlist_tag_filter = None

    playlists = PlaylistRepository().get_proposable_playlists_for_soundboard(request.user, soundboard, filter_search)
    try:
        page_number = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_number = 1

    paginator = Paginator(playlists, 10)
    context = extract_context_to_paginator(paginator, page_number)

    tags = PlaylistTagRepository().get_list_active_tags()
    return render(request, 'Html/Soundboard/modal/soundboard_propose_playlist_list.html', {
        'soundboard': soundboard,
        'page_objects': context['page_objects'],
        'paginator': context['paginator'],
        'playlistType': PlaylistTypeEnum.convert_to_dict(),
        'selected_type': playlist_type_filter,
        'list_playlist_tags_dict': {t.label: t.name for t in tags},
        'selected_playlist_tag': playlist_tag_filter,
    })


@login_required
@require_http_methods(['POST'])
def public_soundboard_propose_playlist(request, soundboard_uuid, playlist_uuid) -> JsonResponse:
    """Propose une playlist de l'utilisateur au propriétaire d'un soundboard public."""
    soundboard = (SoundBoardService(request)).get_public_soundboard(soundboard_uuid)
    if not soundboard:
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

    playlist = PlaylistRepository().get(playlist_uuid)
    if not playlist:
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

    try:
        PlaylistProposalService().propose(playlist, soundboard, request.user)
        return JsonResponse({
            'success': True,
            'message': "Votre proposition a été envoyée au propriétaire du soundboard",
        }, status=201)
    except PlaylistProposalNotEligibleException:
        return JsonResponse({'error': "Cette playlist n'est pas éligible à la proposition"}, status=403)
    except PlaylistProposalAlreadyExistsException:
        return JsonResponse({'error': "Une proposition existe déjà pour cette playlist sur ce soundboard"}, status=409)
    except PlaylistProposalUnauthorizedException as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        logger.error(f"Erreur lors de la proposition de playlist pour soundboard {soundboard_uuid}: {e}")
        return JsonResponse({'error': ErrorMessageEnum.INTERNAL_SERVER_ERROR.value}, status=500)


@login_required
@require_http_methods(['POST'])
def public_soundboard_withdraw_proposal(request, soundboard_uuid, proposal_uuid) -> JsonResponse:
    """Retire une proposition en attente, à l'initiative de son auteur."""
    proposal = PlaylistProposalRepository().get(proposal_uuid)
    if not proposal or str(proposal.soundboard.uuid) != str(soundboard_uuid):
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

    try:
        PlaylistProposalService().withdraw(proposal, request.user)
        return JsonResponse({'success': True, 'message': "Proposition retirée"}, status=200)
    except PlaylistProposalUnauthorizedException as e:
        return JsonResponse({'error': str(e)}, status=403)
    except PlaylistProposalInvalidStatusException as e:
        return JsonResponse({'error': str(e)}, status=409)
    except Exception as e:
        logger.error(f"Erreur lors du retrait de la proposition {proposal_uuid}: {e}")
        return JsonResponse({'error': ErrorMessageEnum.INTERNAL_SERVER_ERROR.value}, status=500)


@login_required
@require_http_methods(['POST'])
def public_soundboard_dismiss_proposal(request, soundboard_uuid, proposal_uuid) -> JsonResponse:
    """Supprime définitivement une proposition refusée, à l'initiative de son auteur."""
    proposal = PlaylistProposalRepository().get(proposal_uuid)
    if not proposal or str(proposal.soundboard.uuid) != str(soundboard_uuid):
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

    try:
        PlaylistProposalService().dismiss(proposal, request.user)
        return JsonResponse({'success': True, 'message': "Proposition supprimée"}, status=200)
    except PlaylistProposalUnauthorizedException as e:
        return JsonResponse({'error': str(e)}, status=403)
    except PlaylistProposalInvalidStatusException as e:
        return JsonResponse({'error': str(e)}, status=409)
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la proposition {proposal_uuid}: {e}")
        return JsonResponse({'error': ErrorMessageEnum.INTERNAL_SERVER_ERROR.value}, status=500)


@login_required
@require_http_methods(['GET'])
def public_soundboard_proposal_stream(request, soundboard_uuid, proposal_uuid) -> HttpResponse | JsonResponse:
    """Stream d'une musique aléatoire de la playlist d'une proposition en attente, réservé à son auteur."""
    cache = CacheFactory.get_default_cache()
    cache_key = f"musicStream:{request.session.session_key}:{soundboard_uuid}:proposal:{proposal_uuid}"
    try:
        if request.headers.get('X-Metadata-Only') == 'true':
            # Requête de suivi pour la durée uniquement : ne doit pas relancer la diffusion partagée.
            proposal = PlaylistProposalRepository().get(proposal_uuid)
            track_id = cache.get(cache_key)
            if proposal and track_id:
                track = TrackRepository().get(track_id, proposal.playlist.uuid)
                if track:
                    return JsonResponse({"duration": track.get_duration()}, status=200)
        else:
            track = (RandomizeTrackService(request)).generate_public_proposal(soundboard_uuid, proposal_uuid)
            if track:
                proposal = PlaylistProposalRepository().get(proposal_uuid)
                SharedSoundboardService(request, soundboard_uuid).proposal_music_start(str(proposal.uuid), str(proposal.playlist.uuid), track)
                cache.set(cache_key, track.id, timeout=60)
                return track.get_reponse_content()
    except Exception as e:
        logger.error(f"Error in public_soundboard_proposal_stream: {e}")
    return HttpResponse(ErrorMessageEnum.ELEMENT_NOT_FOUND.value, status=404)
