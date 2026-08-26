from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from main.domain.common.service.PlaylistProposalService import PlaylistProposalService
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from main.architecture.persistence.repository.PlaylistProposalRepository import PlaylistProposalRepository
from main.architecture.persistence.repository.TrackRepository import TrackRepository
from main.domain.common.exceptions.PlaylistProposalException import (
    PlaylistProposalUnauthorizedException,
    PlaylistProposalInvalidStatusException,
)
from main.domain.common.utils.logger import logger


@login_required
@require_http_methods(['GET'])
def playlist_proposals_list(request):
    """Page dédiée listant les propositions de playlist en attente sur les soundboards de l'utilisateur."""
    track_repository = TrackRepository()
    proposals = PlaylistProposalRepository().get_pending_for_owner(request.user)
    proposals_with_tracks = [(proposal, track_repository.get_tracks_by_playlist(proposal.playlist)) for proposal in proposals]
    return render(request, 'Html/Soundboard/playlist_proposals_list.html', {
        'proposals': proposals,
        'proposals_with_tracks': proposals_with_tracks,
    })


@login_required
@require_http_methods(['GET', 'HEAD'])
def playlist_proposal_track_stream(request, proposal_uuid, music_id) -> HttpResponse | JsonResponse:
    """Stream d'une track d'une playlist proposée, réservé au propriétaire du soundboard ciblé."""
    proposal = PlaylistProposalRepository().get(proposal_uuid)
    if not proposal or proposal.soundboard.user != request.user:
        return HttpResponse(ErrorMessageEnum.ELEMENT_NOT_FOUND.value, status=404)

    track = TrackRepository().get(music_id, proposal.playlist.uuid)
    if not track:
        return HttpResponse(ErrorMessageEnum.ELEMENT_NOT_FOUND.value, status=404)

    try:
        if request.method == 'HEAD':
            response = HttpResponse()
            response['Content-Duration'] = track.get_duration()
            return response
        response = track.get_reponse_content()
        if response:
            return response
    except Exception as e:
        logger.error(f"Error in playlist_proposal_track_stream: {e}")
    return HttpResponse(ErrorMessageEnum.ELEMENT_NOT_FOUND.value, status=404)


@login_required
@require_http_methods(['POST'])
def playlist_proposal_accept(request, proposal_uuid) -> JsonResponse:
    """Accepte une proposition de playlist : duplique et ajoute la playlist au soundboard."""
    proposal = PlaylistProposalRepository().get(proposal_uuid)
    if not proposal:
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

    try:
        PlaylistProposalService().accept(proposal, request.user)
        return JsonResponse({'success': True, 'message': "Proposition acceptée, la playlist a été ajoutée à votre soundboard"}, status=200)
    except PlaylistProposalUnauthorizedException as e:
        return JsonResponse({'error': str(e)}, status=403)
    except PlaylistProposalInvalidStatusException as e:
        return JsonResponse({'error': str(e)}, status=409)
    except Exception as e:
        logger.error(f"Erreur lors de l'acceptation de la proposition {proposal_uuid}: {e}")
        return JsonResponse({'error': ErrorMessageEnum.INTERNAL_SERVER_ERROR.value}, status=500)


@login_required
@require_http_methods(['POST'])
def playlist_proposal_refuse(request, proposal_uuid) -> JsonResponse:
    """Refuse une proposition de playlist."""
    proposal = PlaylistProposalRepository().get(proposal_uuid)
    if not proposal:
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

    try:
        PlaylistProposalService().refuse(proposal, request.user)
        return JsonResponse({'success': True, 'message': "Proposition refusée"}, status=200)
    except PlaylistProposalUnauthorizedException as e:
        return JsonResponse({'error': str(e)}, status=403)
    except PlaylistProposalInvalidStatusException as e:
        return JsonResponse({'error': str(e)}, status=409)
    except Exception as e:
        logger.error(f"Erreur lors du refus de la proposition {proposal_uuid}: {e}")
        return JsonResponse({'error': ErrorMessageEnum.INTERNAL_SERVER_ERROR.value}, status=500)
