from enum import Enum
from django.templatetags.static import static 

class PlaylistTypeEnum(Enum): 
    PLAYLIST_TYPE_INSTANT = 'Instant'
    PLAYLIST_TYPE_AMBIENT = 'Ambient'
    PLAYLIST_TYPE_MUSIC = 'Music'
    
    def get_default_color(self):
        default_color ={
            self.PLAYLIST_TYPE_INSTANT.name: {'color': '#f40b0b', 'colorText': '#ffffff'},
            self.PLAYLIST_TYPE_AMBIENT.name: {'color': '#0bf40d', 'colorText': '#000000'},
            self.PLAYLIST_TYPE_MUSIC.name: {'color': '#0b10f4', 'colorText': '#ffffff'}
        }
        return default_color.get(self.name, {'color': '#000000', 'colorText': '#ffffff'})
 
    def get_icon_class(self):
        default_class ={
            self.PLAYLIST_TYPE_INSTANT.name: "fa-solid fa-explosion",
            self.PLAYLIST_TYPE_AMBIENT.name: "fa-solid fa-dove",
            self.PLAYLIST_TYPE_MUSIC.name: "fa-solid fa-music"
        }
        return default_class.get(self.name, "fa-solid fa-sliders")