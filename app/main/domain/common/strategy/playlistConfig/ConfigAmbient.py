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
            "fadeInDuration": 3,
            "fadeInType": FadeEnum.EASE_IN.value,
            "fadeOutDuration": 3,
            "fadeOutType": FadeEnum.EASE_OUT.value,
            "loop": True,
            "singleConcurrentRead":False,
            "fadeOffOnStopDuration":0.5,
            "fadeOffOnStopType":FadeEnum.LINEAR.value,
            "volume" : 75,
            "delay" : 0
        }