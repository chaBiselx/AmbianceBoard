from enum import Enum
from django.templatetags.static import static 

class PlaylistTypeEnum(Enum): 
    PLAYLIST_TYPE_INSTANT = 'Instant'
    PLAYLIST_TYPE_AMBIENT = 'Ambient'
    PLAYLIST_TYPE_MUSIC = 'Music'
    
    def get_icon_path(self):
        return static(f"img/PlaylistType/icon_{self.value.lower()}.png")