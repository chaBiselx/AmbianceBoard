from home.enum.PlaylistTypeEnum import PlaylistTypeEnum

class ConfigMusic():
    def get_data(self, obj):
        return {
            "type":PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC, 
            "fadeIn": True, 
            "fadeOut": True, 
            "loop": True,
            "singleConcurrentRead":True
        }