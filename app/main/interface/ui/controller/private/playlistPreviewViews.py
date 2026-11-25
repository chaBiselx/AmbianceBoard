from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from main.architecture.persistence.repository.TrackRepository import TrackRepository
from main.domain.common.service.PlaylistService import PlaylistService
from main.domain.common.service.PlaylistPreviewService import PlaylistPreviewService
from main.domain.common.utils.logger import logger


@login_required
@require_GET
@never_cache
def playlist_preview_modal(request, playlist_uuid):
    playlist = PlaylistService(request).get_playlist(playlist_uuid)
    if not playlist or not TrackRepository().get_count(playlist):
        return HttpResponse(status=404)
    return render(request, 'Html/Playlist/modal/playlist_preview.html', {'playlist': playlist})


@login_required
@require_GET
@never_cache
def playlist_preview_stream(request, playlist_uuid):
    metadata_only = request.headers.get('X-Metadata-Only') == 'true'
    track = PlaylistPreviewService(request).get_track(playlist_uuid, metadata_only)
    if track:
        try:
            if metadata_only:
                return JsonResponse({'track_id': track.id, 'name': track.get_name(), 'duration': track.get_duration()})
            response = track.get_reponse_content()
            if response is not None:
                return response
        except Exception:
            logger.error('[playlist_preview_stream] failed')
    return HttpResponse(status=404)