from django.contrib import admin
from home.models.SoundBoard import SoundBoard
from home.models.Playlist import Playlist
from home.models.User import User
from home.models.Music import Music
from home.models.UserModerationLog import UserModerationLog

admin.site.register(SoundBoard)
admin.site.register(Playlist)
admin.site.register(User)
admin.site.register(Music)
admin.site.register(UserModerationLog)
