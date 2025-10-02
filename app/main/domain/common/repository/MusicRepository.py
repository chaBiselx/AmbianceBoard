from typing import Any, Optional, List
from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.User import User
from main.domain.common.repository.filters.MusicFilter import MusicFilter


class MusicRepository:

    def get_music(self, id_music:int) -> Music|None:
        try:
            return Music.objects.get(id=id_music)
        except Music.DoesNotExist:
            return None

    def exist_from_path(self, file_path: str) -> bool:
        return Music.objects.filter(file=file_path).exists()
    
    def get_list_music(self, playlist_uuid: int) -> Optional[List[Music]]:
        try:
            music_filter = MusicFilter() 
            queryset = music_filter.filter_by_user(self.request.user)
            queryset = music_filter.filter_by_playlist(playlist_uuid)
            return queryset
        except Playlist.DoesNotExist:
            return None

