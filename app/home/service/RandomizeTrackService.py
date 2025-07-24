import uuid
from home.enum.PermissionEnum import PermissionEnum
from home.models.Playlist import Playlist
from home.models.Music import Music
from home.models.Track import Track
from home.filters.MusicFilter import MusicFilter
from home.forms.MusicForm import MusicForm
from home.factory.UserParametersFactory import UserParametersFactory
from home.service.SoundBoardService import SoundBoardService
from home.enum.MusicFormatEnum import MusicFormatEnum


class RandomizeTrackService:
    
    def __init__(self, request):
        self.request = request

    def generate_private(self, playlist_uuid:int)-> Music|None :
        try:
            music_filter = MusicFilter()
            music_filter.filter_by_user(self.request.user)
            return self._get_random_music_from_playlist(music_filter, playlist_uuid)
        except Playlist.DoesNotExist:
            return None
    
    def generate_public(self, soundboard_uuid:uuid, playlist_uuid:int)-> Music|None :
        soundboard = (SoundBoardService(self.request)).get_public_soundboard(soundboard_uuid)
        if not soundboard:
            return None
        try:
            music_filter = MusicFilter()
            return self._get_random_music_from_playlist(music_filter, playlist_uuid)
        except Playlist.DoesNotExist:
            return None
        
    def get_shared(self, soundboard_uuid:uuid, playlist_uuid:int, token:str, music_id: int)-> Music|None :
        soundboard = (SoundBoardService(self.request)).get_soundboard_from_shared_soundboard(soundboard_uuid, token)
        if not soundboard:
            return None
        try:
            return Track.objects.get(pk=music_id, playlist__uuid=playlist_uuid)
        except Track.DoesNotExist:
            return None
        except Playlist.DoesNotExist:
            return None
        
    def _get_random_music_from_playlist(self, music_filter:MusicFilter, playlist_uuid:int)-> Music|None :
        queryset = music_filter.filter_by_playlist(playlist_uuid)
        return queryset.order_by('?').first()
        
        
