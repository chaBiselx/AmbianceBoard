from home.enum.PlaylistTypeEnum import PlaylistTypeEnum
from home.enum.FadeEnum import FadeEnum


class ConfigInstant():
    def get_data(self, obj):
        return {
            "id":obj.id, 
            "type":PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.value, 
            "fadeIn": False, 
            "fadeInDuration": 0,
            "fadeInType": FadeEnum.LINEAR.value,
            "fadeOut": False, 
            "fadeOutDuration": 0,
            "fadeOutType": FadeEnum.LINEAR.value,
            "loop": False,
            "singleConcurrentRead" : False,
            "volume" : obj.volume
        }