from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.models.PlaylistColorUser import PlaylistColorUser
from django.core.cache import cache
from parameters import settings


class DefaultColorPlaylistService():
    
    def __init__(self, user):
        self.user = user
    
    def get_list_default_color(self):
        existing_data = {pcu.typePlaylist: pcu for pcu in PlaylistColorUser.objects.filter(user=self.user)}
        
        initial_data = []
        for playlist_type in PlaylistTypeEnum:
            pcu = existing_data.get(playlist_type.name)
            initial_data.append({
                "typePlaylist": playlist_type.name,
                "color": pcu.color if pcu else playlist_type.get_default_color()['color'],
                "colorText": pcu.colorText if pcu else playlist_type.get_default_color()['colorText'],
            })
        return initial_data
    
    
    def get_list_default_color_ajax(self):
        existing_data = {pcu.typePlaylist: pcu for pcu in PlaylistColorUser.objects.filter(user=self.user)}
        
        initial_data = []
        for playlist_type in PlaylistTypeEnum:
            pcu = existing_data.get(playlist_type.name)
            initial_data.append({
                "typePlaylist": playlist_type.value,
                "color": pcu.color if pcu else playlist_type.get_default_color()['color'],
                "colorText": pcu.colorText if pcu else playlist_type.get_default_color()['colorText'],
            })
        return initial_data
    
    def get_default_color(self, playlist_type):
        cache_key = f"default_color:{self.user.id}:{playlist_type}"
        color_found = cache.get(cache_key)
        if color_found:
            return color_found
        
        existing_data = {pcu.typePlaylist: pcu for pcu in PlaylistColorUser.objects.filter(user=self.user, typePlaylist=playlist_type)}
        if existing_data.get(playlist_type):
            color_found = existing_data[playlist_type].color
        else : 
            color_found = PlaylistTypeEnum[playlist_type].get_default_color()['color']
        
        cache.set(cache_key, color_found, timeout=settings.LIMIT_CACHE_DEFAULT)
        return color_found
    
    def get_default_color_text(self, playlist_type):
        cache_key = f"default_color_text:{self.user.id}:{playlist_type}"
        color_text_found = cache.get(cache_key)
        if color_text_found:
            return color_text_found
        
        existing_data = {pcu.typePlaylist: pcu for pcu in PlaylistColorUser.objects.filter(user=self.user, typePlaylist=playlist_type)}
        if existing_data.get(playlist_type):
            color_text_found = existing_data[playlist_type].colorText
        else :
            color_text_found = PlaylistTypeEnum[playlist_type].get_default_color()['colorText']
        cache.set(cache_key, color_text_found, timeout=settings.LIMIT_CACHE_DEFAULT)
        return color_text_found
    