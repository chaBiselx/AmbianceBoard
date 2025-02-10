from django.contrib import admin
from home.models.SoundBoard import SoundBoard
from home.models.Playlist import Playlist
from home.models.User import User
from home.models.Music import Music
from home.models.Soundboard_Playlist import Soundboard_Playlist
from home.models.UserModerationLog import UserModerationLog
from home.models.FailedLoginAttempt import FailedLoginAttempt

admin.site.register(User)
admin.site.register(UserModerationLog)
admin.site.register(FailedLoginAttempt)
admin.site.register(SoundBoard)
admin.site.register(Playlist)
admin.site.register(Music)
admin.site.register(Soundboard_Playlist)
