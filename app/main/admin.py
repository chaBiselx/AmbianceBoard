from django.contrib import admin
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.LinkMusic import LinkMusic
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.UserModerationLog import UserModerationLog
from main.architecture.persistence.models.FailedLoginAttempt import FailedLoginAttempt
from main.architecture.persistence.models.PlaylistColorUser import PlaylistColorUser
from main.architecture.persistence.models.UserPreference import UserPreference
from main.architecture.persistence.models.UserFavoritePublicSoundboard import UserFavoritePublicSoundboard
from main.architecture.persistence.models.ReportContent import ReportContent
from main.architecture.persistence.models.SharedSoundboard import SharedSoundboard
from main.architecture.persistence.models.Tag import Tag
from main.architecture.persistence.models.UserTier import UserTier
from main.architecture.persistence.models.UserTierHistory import UserTierHistory
from main.architecture.persistence.models.DomainBlacklist import DomainBlacklist
from main.architecture.persistence.models.GeneralNotification import GeneralNotification
from main.architecture.persistence.models.UserNotificationDismissal import UserNotificationDismissal
from main.architecture.persistence.models.UserActivity import UserActivity
from main.architecture.persistence.models.UserDevicePreference import UserDevicePreference


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
admin.site.register(UserActivity)
admin.site.register(UserDevicePreference)
