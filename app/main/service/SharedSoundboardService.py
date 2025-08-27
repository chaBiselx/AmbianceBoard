
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.urls import reverse

from main.architecture.persistence.models.SharedSoundboard import SharedSoundboard
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.domain.common.utils.logger import logger
from main.domain.common.utils.cache.CacheFactory import CacheFactory
from main.domain.common.repository.SoundBoardRepository import SoundBoardRepository
from main.domain.common.repository.SharedSoundboardRepository import SharedSoundboardRepository

class SharedSoundboardService():
    
    def __init__(self, request, soundboard_uuid):
        self.token = request.COOKIES.get('WebSocketToken')
        self.soundboard_uuid = soundboard_uuid
        self.group_name = f"soundboard_{soundboard_uuid}_{self.token}"
        self.cache = CacheFactory.get_default_cache()
        self.soundboard_repository = SoundBoardRepository()


    def music_start(self, playlist_uuid, music):
        if(self._get_shared_soundboard()):
            self._diffuser_message(
                {
                    "type": "music_start",
                    "track": music.id,
                    'url_music': reverse('sharedStreamMusic', args=[self.soundboard_uuid, self.token, playlist_uuid, music.id]),
                    "playlist_uuid": str(playlist_uuid),
                }
            )
            
    def music_stop_all(self):
        if(self._get_shared_soundboard()):
            self._diffuser_message(
                {
                    "type": "music_stop_all",
                    "track": None,
                    "playlist_uuid": None,
                }
            )

    def _diffuser_message(self, message):
        channel_layer = get_channel_layer()
                    
        # Diffuser le message
        async_to_sync(channel_layer.group_send)(
            self.group_name,
            message
        )
        
    def _get_shared_soundboard(self):
        """Récupère le SharedSoundboard de manière asynchrone"""
        cache_key = f"shared_soundboard:{self.soundboard_uuid}:{self.token}"
        shared_soundboard = self.cache.get(cache_key)
        if shared_soundboard is not None:
            return True
            
        if self.token is None:
            return False
        
        try:
            soundboard = self.soundboard_repository.get_from_uuid(self.soundboard_uuid)
            if not soundboard:
                return False

            shared_soundboard = SharedSoundboardRepository().get(
                soundboard=soundboard,
                token=self.token
            )

            if not shared_soundboard:
                logger.error(f"Soundboard introuvable: {self.soundboard_uuid} {self.token}")
                return False

            self.cache.set(cache_key, shared_soundboard)
            return True

        except Exception as e:
            logger.error(f"Erreur lors de la récupération du soundboard: {e}")
            return False
        