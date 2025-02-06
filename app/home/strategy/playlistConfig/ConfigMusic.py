from home.enum.PlaylistTypeEnum import PlaylistTypeEnum

class ConfigMusic():
    def get_data(self, obj):
        return {
            "id":obj.id, 
            "type":PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.value, 
            "fadeIn": True, 
            "fadeInDuration": 5,
            "fadeOut": True, 
            "fadeOutDuration": 5,
            "loop": True,
            "singleConcurrentRead":True,
            "volume" : obj.volume
        }