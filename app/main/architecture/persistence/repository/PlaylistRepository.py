from typing import Any, Optional, List

from django.db.models import Avg, Count
from django.db import models
from django.db.models import QuerySet


from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.filters.PlaylistFilter import PlaylistFilter

class PlaylistRepository:

    def get(self, playlist_uuid: int) -> Optional[Playlist]:
        try:
            return Playlist.objects.get(uuid=playlist_uuid)
        except Playlist.DoesNotExist:
            return None
        
    def count_private(self, user: User) -> int:
        return Playlist.objects.filter(user=user).count()

    def get_listing_playlist(self, user:User, filter:dict) -> List[Playlist]:
        try:
            QuerySet = Playlist.objects.all()
            if 'typePlaylist' in filter:
                QuerySet = QuerySet.filter(typePlaylist=filter['typePlaylist'])
            return QuerySet.filter(user=user).order_by('updated_at') 
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
        
    def file_exists(self, file_path: str) -> bool:
        return Playlist.objects.filter(icon=file_path).exists()

    def get_all_queryset(self) -> QuerySet:
        return Playlist.objects.all()
    
    def get_default_volume_by_playlist(self, soundboard_uid: int):
        try:
            queryset = Playlist.objects.filter(soundboards__uuid=soundboard_uid).values('uuid', 'volume')
            result = {}
            for entry in queryset:
                result[str(entry['uuid'])] = {'volume':entry['volume']}
            return result
        except Exception:
            return []
