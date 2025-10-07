from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from main.service.SoundBoardService import SoundBoardService
from main.domain.common.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository
from main.domain.common.utils.UserTierManager import UserTierManager
from main.domain.common.utils.logger import logger
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.domain.private.dto.UpdateSoundPlaylistDto import UpdateSoundPlaylistDto
from main.domain.private.service.SoundboardPlaylistOptionService import SoundboardPlaylistOptionService

from main.service.SoundBoardService import SoundBoardService


@login_required
@require_http_methods([ 'GET'])
def list_playlists_for_specific_action(request, soundboard_uuid):
    """Pour voir la liste des boutons pour avec des actions spécifiques"""
    shared_playlist_playable_by_shared_user = UserTierManager.can_boolean(request.user, 'shared_playlist_playable_by_shared_user')
    if not shared_playlist_playable_by_shared_user:
        return render(request, HtmlDefaultPageEnum.ERROR_403.value, status=403)
    
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if not soundboard:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    
    
    ordered_soundboard_playlist = SoundboardPlaylistRepository().get_soundboard_playlist_formated(soundboard)
    return render(request, 'Html/Soundboard/list_playlists_for_specific_action.html', {
        'ordered_soundboard_playlist': ordered_soundboard_playlist,
        'soundboard': soundboard
    })
    
@login_required
@require_http_methods(['UPDATE'])
def update_specific_actionable_playlists(request):
    """Met a jour les playlists actionnables par les joueurs"""
    shared_playlist_playable_by_shared_user = UserTierManager.can_boolean(request.user, 'shared_playlist_playable_by_shared_user')
    if not shared_playlist_playable_by_shared_user:
        return JsonResponse({'error': 'Permission refusée'}, status=403)
    
    try:
        update_dto = UpdateSoundPlaylistDto.from_request(request)
        update_service = SoundboardPlaylistOptionService([update_dto])
        update_service.update_playlists()
        if not update_service.is_valid:
            return JsonResponse({'error': 'Données invalides'}, status=400)
        return JsonResponse({'message': 'Mise à jour réussie'})
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des playlists actionnables: {e}")
        return JsonResponse({'error': 'Erreur interne du serveur'}, status=500)
