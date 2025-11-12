from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.enum.FadeEnum import FadeEnum
from main.domain.common.strategy.playlistConfig.AbstractConfig import AbstractConfig

class ConfigAmbient(AbstractConfig):
    def __init__(self):
        super().__init__()
        self.default_data = {
            "id": None, 
            "type": PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.value, 
            "durationRemainingTriggerNextMusic": 4,
            "fadeIn": True, 
            "fadeInDuration": 3,
            "fadeInType": FadeEnum.EASE_IN.value,
            "fadeOut": True, 
            "fadeOutDuration": 3,
            "fadeOutType": FadeEnum.EASE_IN.value,
            "loop": True,
            "singleConcurrentRead":False,
            "fadeOffOnStop":True,
            "fadeOffOnStopDuration":0.5,
            "fadeOffOnStopType":FadeEnum.LINEAR.value,
            "volume" : 75,
            "delay" : 0
        }