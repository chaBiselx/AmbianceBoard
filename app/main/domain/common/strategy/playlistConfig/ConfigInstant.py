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
            "fadeIn": False, 
            "fadeInDuration": 0,
            "fadeInType": FadeEnum.LINEAR.value,
            "fadeOut": False, 
            "fadeOutDuration": 0,
            "fadeOutType": FadeEnum.LINEAR.value,
            "loop": False,
            "singleConcurrentRead" : False,
            "fadeOffOnStop":False,
            "fadeOffOnStopDuration":0,
            "fadeOffOnStopType":FadeEnum.LINEAR.value,
            "volume" : 75,
            "delay" :  0
        }