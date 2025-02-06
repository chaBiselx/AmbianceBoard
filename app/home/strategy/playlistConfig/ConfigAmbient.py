from home.enum.PlaylistTypeEnum import PlaylistTypeEnum

class ConfigAmbient():
    def get_data(self, obj):
        return {
            "id":obj.id, 
            "type":PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.value, 
            "fadeIn": True, 
            "fadeInDuration": 3,
            "fadeOut": True, 
            "fadeOutDuration": 3,
            "loop": True,
            "singleConcurrentRead":False,
            "volume" : obj.volume
        }