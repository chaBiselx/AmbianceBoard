
import logging

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.urls import reverse

from home.models.SharedSoundboard import SharedSoundboard
from home.models.SoundBoard import SoundBoard


logger = logging.getLogger('home')

class SharedSoundboardService():
    
    def __init__(self, request, soundboard_uuid):
        self.token = request.COOKIES.get('WebSocketToken')
        self.soundboard_uuid = soundboard_uuid
        self.group_name = f"soundboard_{soundboard_uuid}_{self.token}"
        
    
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
  
    def music_stop(self, playlist_uuid):
        if(self._get_shared_soundboard()):
            self._diffuser_message(
                {
                    "type": "music_stop",
                    "track": None,
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
        if self.token is None:
            return False
        
        #TODO use CACHE
        
        try:
            soundboard = SoundBoard.objects.get(uuid=self.soundboard_uuid)
            if not soundboard:
                return False
            
            SharedSoundboard.objects.get(
                soundboard=soundboard, 
                token=self.token
            )
            return True
        except SharedSoundboard.DoesNotExist:
            logger.error(f"Soundboard introuvable: {self.soundboard_uuid}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du soundboard: {e}")
            return False
        