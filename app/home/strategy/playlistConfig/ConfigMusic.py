from home.enum.PlaylistTypeEnum import PlaylistTypeEnum
from home.enum.FadeEnum import FadeEnum

class ConfigMusic():
    def get_data(self, playlist):
        return {
            "id": playlist.id, 
            "type": PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.value, 
            "fadeIn": True, 
            "fadeInDuration": 5,
            "fadeInType": FadeEnum.EASE.value,
            "fadeOut": True, 
            "fadeOutDuration": 5,
            "fadeOutType": FadeEnum.EASE.value,
            "loop": True,
            "singleConcurrentRead":True,
            "volume" : playlist.volume,
            "delay" : playlist.maxDelay or 0
        }