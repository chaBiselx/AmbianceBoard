from home.enum.PlaylistTypeEnum import PlaylistTypeEnum


class ConfigInstant():
    def get_data(self, obj):
        return {
            "id":obj.id, 
            "type":PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT, 
            "fadeIn": False, 
            "fadeOut": False, 
            "loop": False,
            "singleConcurrentRead" : False,
            "volume" : obj.volume
        }