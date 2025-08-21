from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.enum.FadeEnum import FadeEnum
from main.strategy.playlistConfig.AbstractConfig import AbstractConfig

class ConfigMusic(AbstractConfig):
    def __init__(self):
        super().__init__()
        self.default_data = {
            "id": None, 
            "type": PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.value, 
            "fadeIn": True, 
            "fadeInDuration": 5,
            "fadeInType": FadeEnum.EASE.value,
            "fadeOut": True, 
            "fadeOutDuration": 5,
            "fadeOutType": FadeEnum.EASE.value,
            "loop": True,
            "singleConcurrentRead":True,
            "volume" : 75,
            "delay" : 0
        }
        
