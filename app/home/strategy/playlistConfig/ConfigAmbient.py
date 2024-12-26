from home.enum.PlaylistTypeEnum import PlaylistTypeEnum

class ConfigAmbient():
    def get_data(self, obj):
        return {
            "type":PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT, 
            "fadeIn": True, 
            "fadeOut": True, 
            "loop": True,
            "singleConcurrentRead":True,
            "volume" : obj.volume
        }