from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.enum.FadeEnum import FadeEnum
from main.domain.common.strategy.playlistConfig.AbstractConfig import AbstractConfig

class ConfigInstant(AbstractConfig):
    def __init__(self):
        super().__init__()
        self.default_data = {
            "id": None, 
            "type": PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.value, 
            "durationRemainingTriggerNextMusic": 0,
            "fadeInDuration": 0,
            "fadeInType": FadeEnum.DISABLED.value,
            "fadeOutDuration": 0,
            "fadeOutType": FadeEnum.DISABLED.value,
            "loop": False,
            "singleConcurrentRead" : False,
            "fadeOffOnStopDuration":0,
            "fadeOffOnStopType":FadeEnum.DISABLED.value,
            "volume" : 75,
            "delay" :  0
        }