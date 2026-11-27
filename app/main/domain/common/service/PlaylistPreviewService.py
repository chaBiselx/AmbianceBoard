from main.architecture.persistence.repository.TrackRepository import TrackRepository
from main.domain.common.service.PlaylistService import PlaylistService
from main.domain.common.service.RandomizeTrackService import RandomizeTrackService
from main.domain.common.utils.cache.CacheFactory import CacheFactory


class PlaylistPreviewService:
    def __init__(self, request):
        self.request = request
        self.repository = TrackRepository()

    def get_track(self, playlist_uuid, metadata_only=False):
        playlist = PlaylistService(self.request).get_playlist(playlist_uuid)
        playback_id = self.request.GET.get('i', '')
        if not playlist or not playback_id or len(playback_id) > 64 or not playback_id.replace('-', '').isalnum():
            return None
        cache = CacheFactory.get_default_cache()
        key = f"playlistPreview:{self.request.user.pk}:{self.request.session.session_key}:{playlist.uuid}:{playback_id}"
        track_id = cache.get(key)
        if track_id:
            return self.repository.get(track_id, playlist.uuid)
        if metadata_only:
            return None
        track = RandomizeTrackService(self.request).generate_playlist_preview(playlist.uuid)
        if track:
            cache.set(key, track.id, timeout=3600)
        return track