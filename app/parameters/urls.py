from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from home.views.generalViews import home, create_account, login_view, logout_view, resend_email_confirmation, send_reset_password, token_validation_reset_password, legal_notice
from home.views.privateViews import soundboard_list, soundboard_create, soundboard_read, soundboard_update, soundboard_delete, soundboard_organize, soundboard_organize_update
from home.views.privateViews import playlist_create, playlist_read_all, playlist_create_with_soundboard, playlist_update, playlist_delete, playlist_listing_colors, playlist_describe_type
from home.views.privateViews import music_create, music_update, music_delete,music_stream, update_direct_volume
from home.views.moderatorViews import moderator_dashboard, moderator_listing_images_playlist, moderator_listing_images_soundboard, moderator_get_infos_playlist, moderator_get_infos_soundboard, moderator_listing_log_moderation, moderator_get_infos_user
from home.views.settingsViews import settings_index, settings_update_default_style
from home.views.managerViews import manager_dashboard, clean_media_folder
from home.views.publicViews import public_index, public_listing_soundboard, public_soundboard_read_playlist, public_music_stream
from home.views.confirmViews import confirm_account

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("legal-notice", legal_notice, name="legalNotice"),
    
    path("create-account/", create_account, name="createAccount"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("resend-email/", resend_email_confirmation, name="resend_email_confirmation"),
    path("resend-email/confirm/<uuid:uuid_user>/<uuid:confirmation_token>", confirm_account, name="confirm_account"),
    path("reset-password", send_reset_password, name="send_reset_password"),
    path("reset-password/validate/<uuid:uuid_user>/<str:token_reinitialisation>", token_validation_reset_password, name="token_validation_reset_password"),
    
    path("soundBoards/", soundboard_list, name="soundboardsList"),
    path("soundBoards/new", soundboard_create, name="soundboardsNew"),
    path("soundBoards/<uuid:soundboard_uuid>", soundboard_read, name="soundboardsRead"),
    path("soundBoards/<uuid:soundboard_uuid>/update", soundboard_update, name="soundboardsUpdate"),
    path("soundBoards/<uuid:soundboard_uuid>/delete", soundboard_delete, name="soundboardsDelete"),
    path("soundBoards/<uuid:soundboard_uuid>/organize", soundboard_organize, name="organizeSoundboard"),
    path("soundBoards/<uuid:soundboard_uuid>/organize/update", soundboard_organize_update, name="organizeSoundboardUpdate"),
    
    path('account/settings/',settings_index, name="settingsIndex"),
    path('account/settings/playlists/style',settings_update_default_style, name="defaultPlaylistType"),
    
    path("soundBoards/<uuid:soundboard_uuid>/music/create", playlist_create_with_soundboard, name="addPlaylistWithSoundboard"),
    path("playlist/create", playlist_create, name="addPlaylist"),
    path("playlist/all", playlist_read_all, name="playlistsAllList"),
    path("playlist/<uuid:playlist_uuid>/update", playlist_update, name="playlistUpdate"),
    path("playlist/<uuid:playlist_uuid>/delete", playlist_delete, name="playlistDelete"),
    path("playlist/type/describe", playlist_describe_type, name="playlistDescribeType"),
    
    path("playlist/<uuid:playlist_uuid>/music/create", music_create, name="addMusic"),
    path("playlist/<uuid:playlist_uuid>/music/edit/<int:music_id>", music_update, name="editMusic"),
    path("playlist/<uuid:playlist_uuid>/music/delete/<int:music_id>", music_delete, name="deleteMusic"),
    path("playlist/<uuid:playlist_uuid>/stream", music_stream, name="streammMusic"),
    path("playlist/<uuid:playlist_uuid>/volume/update", update_direct_volume, name="update_direct_volume"),
    
    path("playlist/other-colors", playlist_listing_colors, name="getListingOtherColors"),
    
    path("public/", public_index, name="publicIndex"),
    path("public/soundboards", public_listing_soundboard, name="publicListingSoundboard"),
    path("public/soundboards/<uuid:soundboard_uuid>", public_soundboard_read_playlist, name="publicReadSoundboard"),
    path("public/soundboards/<uuid:soundboard_uuid>/<uuid:playlist_uuid>/stream", public_music_stream, name="publicStreammMusic"),
    
    
    
    path("moderator/", moderator_dashboard, name="moderatorDashboard"),
    path("moderator/playlist/images", moderator_listing_images_playlist, name="moderatorControleImagesPlaylist"),
    path("moderator/playlist/<uuid:playlist_uuid>", moderator_get_infos_playlist, name="moderatorGetDataPlaylist"),
    path("moderator/soundboard/images", moderator_listing_images_soundboard, name="moderatorControleImagesSoundboard"),
    path("moderator/soundboard/<uuid:soundboard_uuid>", moderator_get_infos_soundboard, name="moderatorGetDataSoundboard"),
    path("moderator/log/", moderator_listing_log_moderation, name="moderatorControleLog"),
    path("moderator/log/user/<uuid:user_uuid>", moderator_get_infos_user, name="moderatorGetDataUser"),
    
    path("manager/", manager_dashboard, name="managerDashboard"),
    path("manager/clean-media-folders", clean_media_folder, name="adminCleanMediaFolders"),
    
]


if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
# debug toolbar
if bool(settings.DEBUG_TOOLBAR): 
    from django.conf.urls import include
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns