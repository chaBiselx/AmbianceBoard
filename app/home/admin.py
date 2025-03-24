from django.contrib import admin
from home.models.SoundBoard import SoundBoard
from home.models.Playlist import Playlist
from home.models.User import User
from home.models.Music import Music
from home.models.SoundboardPlaylist import SoundboardPlaylist
from home.models.UserModerationLog import UserModerationLog
from home.models.FailedLoginAttempt import FailedLoginAttempt
from home.models.PlaylistColorUser import PlaylistColorUser
from home.models.UserPreference import UserPreference
from home.models.UserFavoritePublicSoundboard import UserFavoritePublicSoundboard

admin.site.register(User)
admin.site.register(UserModerationLog)
admin.site.register(FailedLoginAttempt)
admin.site.register(SoundBoard)
admin.site.register(Playlist)
admin.site.register(Music)
admin.site.register(SoundboardPlaylist)
admin.site.register(PlaylistColorUser)
admin.site.register(UserPreference)
admin.site.register(UserFavoritePublicSoundboard)
