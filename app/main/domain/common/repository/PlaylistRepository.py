from typing import Any, Optional, List

from django.db.models import Avg, Count
from django.db import models

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User
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


    def get_stat_nb_track_per_playlist(self) -> int : 
        return Playlist.objects.annotate(
        music_count=models.Count('tracks')
        ).aggregate(avg_music=Avg('music_count'))['avg_music']
    
    def delete(self, playlist: Playlist) -> None:
        playlist.delete()
