from home.enum.PlaylistTypeEnum import PlaylistTypeEnum
from home.enum.FadeEnum import FadeEnum


class ConfigAmbient():
    def get_data(self, playlist):
        return {
            "id": playlist.id, 
            "type": PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.value, 
            "fadeIn": True, 
            "fadeInDuration": 3,
            "fadeInType": FadeEnum.EASE_IN.value,
            "fadeOut": True, 
            "fadeOutDuration": 3,
            "fadeOutType": FadeEnum.EASE_IN.value,
            "loop": True,
            "singleConcurrentRead":False,
            "volume" : playlist.volume,
            "delay" : playlist.maxDelay or 0
        }