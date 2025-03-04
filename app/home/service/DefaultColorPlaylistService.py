from home.enum.PlaylistTypeEnum import PlaylistTypeEnum
from home.models.PlaylistColorUser import PlaylistColorUser


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
        existing_data = {pcu.typePlaylist: pcu for pcu in PlaylistColorUser.objects.filter(user=self.user, typePlaylist=playlist_type)}
        if existing_data.get(playlist_type):
            return existing_data[playlist_type].color
        return PlaylistTypeEnum[playlist_type].get_default_color()['color']
    
    def get_default_color_text(self, playlist_type):
        existing_data = {pcu.typePlaylist: pcu for pcu in PlaylistColorUser.objects.filter(user=self.user, typePlaylist=playlist_type)}
        if existing_data.get(playlist_type):
            return existing_data[playlist_type].colorText
        return PlaylistTypeEnum[playlist_type].get_default_color()['colorText']
    