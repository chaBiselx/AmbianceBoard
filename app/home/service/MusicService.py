import logging
from ..models.Playlist import Playlist
from ..models.Music import Music
from ..filters.MusicFilter import MusicFilter

class MusicService:
    
    def __init__(self, request):
        self.request = request
    
    def get_random_music(self, playlist_id:int)-> Music|None :
        try:
            music_filter = MusicFilter()
            queryset = music_filter.filter_by_user(self.request.user)
            queryset = music_filter.filter_by_playlist(playlist_id)
            return queryset.order_by('?').first()
        except Playlist.DoesNotExist:
            return None
        

        