import uuid
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.Track import Track
from main.domain.common.repository.filters.MusicFilter import MusicFilter
from main.domain.common.repository.TrackRepository import TrackRepository
from main.forms.MusicForm import MusicForm
from main.domain.common.factory.UserParametersFactory import UserParametersFactory
from main.service.SoundBoardService import SoundBoardService
from main.domain.common.enum.MusicFormatEnum import MusicFormatEnum


class RandomizeTrackService:
    
    def __init__(self, request):
        self.request = request
        self.track_repository = TrackRepository()

    def generate_private(self, playlist_uuid:int)-> Music|None :
        try:
            return self.track_repository.get_random_private(playlist_uuid, self.request.user)
        except Playlist.DoesNotExist:
            return None
    
    def generate_public(self, soundboard_uuid:uuid, playlist_uuid:int)-> Music|None :
        soundboard = (SoundBoardService(self.request)).get_public_soundboard(soundboard_uuid)
        if not soundboard:
            return None
        try:
            return self.track_repository.get_random_public(playlist_uuid)
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

        
        
