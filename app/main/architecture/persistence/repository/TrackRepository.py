from typing import Any, Optional, List
from main.architecture.persistence.models.Track import Track
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.Playlist import Playlist
from django.utils import timezone
from main.architecture.persistence.repository.filters.MusicFilter import MusicFilter


class TrackRepository:

    def get(self, music_id: str, playlist_uuid: str) -> Track|None:
        try:
            return Track.objects.get(pk=music_id, playlist__uuid=playlist_uuid)
        except Track.DoesNotExist:
            return None
        except Playlist.DoesNotExist:
            return None

    def get_count(self, playlist: Playlist) -> int:
        return Track.objects.filter(playlist=playlist).count()
    
    def get_random_private(self, playlist_uuid:int, user:User) -> Track|None:
        music_filter = MusicFilter()
        music_filter.filter_by_user(user)
        return self._get_random_music_from_playlist(music_filter, playlist_uuid)

    def get_random_public(self, playlist_uuid:int) -> Track|None:
        music_filter = MusicFilter()
        return self._get_random_music_from_playlist(music_filter, playlist_uuid)

    def _get_random_music_from_playlist(self, music_filter:MusicFilter, playlist_uuid:int)-> Track|None :
        try:
            queryset = music_filter.filter_by_playlist(playlist_uuid)
            return queryset.order_by('?').first()
        except Track.DoesNotExist :
            return None


