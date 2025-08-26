from typing import Any, Optional, List
from main.models.Playlist import Playlist
from main.models.User import User
from main.domain.common.repository.filters.PlaylistFilter import PlaylistFilter


class PlaylistRepository:

    def get(self, playlist_uuid: int) -> Optional[Playlist]:
        try:
            return Playlist.objects.get(uuid=playlist_uuid)
        except Playlist.DoesNotExist:
            return None

    def get_all_private(self, user:User) -> List[Playlist]:
        try:
            _query_set = Playlist.objects.all().order_by('updated_at') 
            _filter = PlaylistFilter(queryset=_query_set)
            return _filter.filter_by_user(user)
        except Exception:
            return []
        
    def count_private(self, user:User) -> int:
        return Playlist.objects.filter(user=user).count()

    def get_distinct_styles(self) -> List[str]:
        return Playlist.objects.values('colorText', 'color', 'typePlaylist').distinct().all()

    def delete(self, playlist: Playlist) -> None:
        playlist.delete()
