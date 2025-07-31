from main.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.enum.FadeEnum import FadeEnum
from main.strategy.playlistConfig.AbstractConfig import AbstractConfig

class ConfigInstant(AbstractConfig):
    def __init__(self):
        super().__init__()
        self.default_data = {
            "id": None, 
            "type": PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.value, 
            "fadeIn": False, 
            "fadeInDuration": 0,
            "fadeInType": FadeEnum.LINEAR.value,
            "fadeOut": False, 
            "fadeOutDuration": 0,
            "fadeOutType": FadeEnum.LINEAR.value,
            "loop": False,
            "singleConcurrentRead" : False,
            "volume" : 75,
            "delay" :  0
        }