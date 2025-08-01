from django.contrib import admin
from main.models.SoundBoard import SoundBoard
from main.models.Playlist import Playlist
from main.models.User import User
from main.models.Music import Music
from main.models.LinkMusic import LinkMusic
from main.models.SoundboardPlaylist import SoundboardPlaylist
from main.models.UserModerationLog import UserModerationLog
from main.models.FailedLoginAttempt import FailedLoginAttempt
from main.models.PlaylistColorUser import PlaylistColorUser
from main.models.UserPreference import UserPreference
from main.models.UserFavoritePublicSoundboard import UserFavoritePublicSoundboard
from main.models.ReportContent import ReportContent
from main.models.SharedSoundboard import SharedSoundboard
from main.models.Tag import Tag
from main.models.UserTier import UserTier
from main.models.UserTierHistory import UserTierHistory
from main.models.DomainBlacklist import DomainBlacklist
from main.models.GeneralNotification import GeneralNotification
from main.models.UserNotificationDismissal import UserNotificationDismissal

admin.site.register(User)
admin.site.register(UserModerationLog)
admin.site.register(FailedLoginAttempt)
admin.site.register(SoundBoard)
admin.site.register(Playlist)
admin.site.register(Music)
admin.site.register(LinkMusic)
admin.site.register(SoundboardPlaylist)
admin.site.register(PlaylistColorUser)
admin.site.register(UserPreference)
admin.site.register(UserFavoritePublicSoundboard)
admin.site.register(ReportContent)
admin.site.register(SharedSoundboard)
admin.site.register(Tag)
admin.site.register(UserTier)
admin.site.register(UserTierHistory)
admin.site.register(DomainBlacklist)
admin.site.register(GeneralNotification)
admin.site.register(UserNotificationDismissal)
