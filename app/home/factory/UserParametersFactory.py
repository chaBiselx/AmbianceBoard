

from parameters import settings
from home.models.User import User
from home.enum.PermissionEnum import PermissionEnum

class UserParametersFactory:
    prefix_permission = "auth."
    limit_soundboard = settings.LIMIT_USER_STANDARD_SOUNDBOARD
    limit_playlist = settings.LIMIT_USER_STANDARD_PLAYLIST
    limit_music_per_playlist = settings.LIMIT_USER_STANDARD_MUSIC_PER_PLAYLIST
    limit_weight_file = settings.LIMIT_USER_STANDARD_WEIGHT_MUSIC

    def __init__(self, user:User): 
        self._user = user
        self._set_limit_soundboard()
        self._set_limit_playlist()
        self._set_limit_music_per_playlist()
        self._set_limit_weight_file()

    def _set_limit_soundboard(self):
        if(self._user.has_perm(self.prefix_permission + PermissionEnum.USER_PREMIUM_OVER_LIMIT_SOUNDBOARD.name)):  
            self.limit_soundboard = settings.LIMIT_USER_PREMIUM_SOUNDBOARD

    def _set_limit_playlist(self):
        if(self._user.has_perm(self.prefix_permission + PermissionEnum.USER_PREMIUM_OVER_LIMIT_PLAYLIST.name)):  
            self.limit_playlist = settings.LIMIT_USER_PREMIUM_PLAYLIST

    def _set_limit_music_per_playlist(self):
        if(self._user.has_perm(self.prefix_permission + PermissionEnum.USER_PREMIUM_OVER_LIMIT_MUSIC_PER_PLAYLIST.name)):  
            self.limit_music_per_playlist = settings.LIMIT_USER_PREMIUM_MUSIC_PER_PLAYLIST        
    
    def _set_limit_weight_file(self):
        if(self._user.has_perm(self.prefix_permission + PermissionEnum.USER_PREMIUM_OVER_LIMIT_WEIGHT_MUSIC.name)):  
            self.limit_weight_file = settings.LIMIT_USER_PREMIUM_WEIGHT_MUSIC
