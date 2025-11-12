from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.enum.FadeEnum import FadeEnum
from main.domain.common.strategy.playlistConfig.AbstractConfig import AbstractConfig

class ConfigMusic(AbstractConfig):
    def __init__(self):
        super().__init__()
        self.default_data = {
            "id": None, 
            "type": PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.value, 
            "durationRemainingTriggerNextMusic": 6,
            "fadeIn": True, 
            "fadeInDuration": 5,
            "fadeInType": FadeEnum.EASE.value,
            "fadeOut": True, 
            "fadeOutDuration": 5,
            "fadeOutType": FadeEnum.EASE.value,
            "loop": True,
            "singleConcurrentRead":True,
            "fadeOffOnStop":True,
            "fadeOffOnStopDuration":2,
            "fadeOffOnStopType":FadeEnum.EASE_IN.value,
            "volume" : 75,
            "delay" : 0
        }
        
