from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from home.views.generalViews import home, create_account, login_view, logout_view, resend_email_confirmation, send_reset_password, token_validation_reset_password
from home.views.privateViews import soundboard_list, soundboard_create, soundboard_read, soundboard_update, soundboard_delete, soundboard_organize, soundboard_organize_update
from home.views.privateViews import playlist_create, playlist_read_all, playlist_create_with_soundboard, playlist_update, playlist_delete, playlist_listing_colors
from home.views.privateViews import music_create, music_update, music_delete,music_stream
from home.views.moderatorViews import moderator_dashboard, moderator_listing_images_playlist, moderator_listing_images_soundboard, moderator_get_infos_playlist, moderator_get_infos_soundboard, moderator_listing_log_moderation, moderator_get_infos_user
from home.views.managerViews import manager_dashboard, clean_media_folder
from home.views.publicViews import public_index, public_listing_soundboard, public_soundboard_read_playlist, public_music_stream
from home.views.staticProtectedViews import static_protected_moderator_js, static_protected_manager_js
from home.views.confirmViews import confirm_account

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    
    path("create-account/", create_account, name="createAccount"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("resend-email/", resend_email_confirmation, name="resend_email_confirmation"),
    path("resend-email/confirm/<uuid:uuid_user>/<uuid:confirmation_token>", confirm_account, name="confirm_account"),
    path("reset-password", send_reset_password, name="send_reset_password"),
    path("reset-password/validate/<uuid:uuid_user>/<str:token_reinitialisation>", token_validation_reset_password, name="token_validation_reset_password"),
    
    path("soundBoards/", soundboard_list, name="soundboardsList"),
    path("soundBoards/new", soundboard_create, name="soundboardsNew"),
    path("soundBoards/<uuid:soundboard_id>", soundboard_read, name="soundboardsRead"),
    path("soundBoards/<uuid:soundboard_id>/update", soundboard_update, name="soundboardsUpdate"),
    path("soundBoards/<uuid:soundboard_id>/delete", soundboard_delete, name="soundboardsDelete"),
    path("soundBoards/<uuid:soundboard_id>/organize", soundboard_organize, name="organizeSoundboard"),
    path("soundBoards/<uuid:soundboard_id>/organize/update", soundboard_organize_update, name="organizeSoundboardUpdate"),
    
    path("soundBoards/<uuid:soundboard_id>/music/create", playlist_create_with_soundboard, name="addPlaylistWithSoundboard"),
    path("playlist/create", playlist_create, name="addPlaylist"),
    path("playlist/all", playlist_read_all, name="playlistsAllList"),
    path("playlist/<uuid:playlist_id>/update", playlist_update, name="playlistUpdate"),
    path("playlist/<uuid:playlist_id>/delete", playlist_delete, name="playlistDelete"),
    
    path("playlist/<uuid:playlist_id>/music/create", music_create, name="addMusic"),
    path("playlist/<uuid:playlist_id>/music/edit/<int:music_id>", music_update, name="editMusic"),
    path("playlist/<uuid:playlist_id>/music/delete/<int:music_id>", music_delete, name="deleteMusic"),
    path("playlist/<uuid:playlist_id>/stream", music_stream, name="streammMusic"),
    path("playlist/other-colors", playlist_listing_colors, name="getListingOtherColors"),
    
    path("public/", public_index, name="publicIndex"),
    path("public/soundboards", public_listing_soundboard, name="publicListingSoundboard"),
    path("public/soundboards/<uuid:soundboard_id>", public_soundboard_read_playlist, name="publicReadSoundboard"),
    path("public/soundboards/<uuid:soundboard_id>/<uuid:playlist_id>/stream", public_music_stream, name="publicStreammMusic"),
    
    
    
    path("moderator/", moderator_dashboard, name="moderatorDashboard"),
    path("moderator/playlist/images", moderator_listing_images_playlist, name="moderatorControleImagesPlaylist"),
    path("moderator/playlist/<uuid:playlist_id>", moderator_get_infos_playlist, name="moderatorGetDataPlaylist"),
    path("moderator/soundboard/images", moderator_listing_images_soundboard, name="moderatorControleImagesSoundboard"),
    path("moderator/soundboard/<uuid:soundboard_id>", moderator_get_infos_soundboard, name="moderatorGetDataSoundboard"),
    path("moderator/log/", moderator_listing_log_moderation, name="moderatorControleLog"),
    path("moderator/log/user/<uuid:user_id>", moderator_get_infos_user, name="moderatorGetDataUser"),
    
    
    
    path("protected/static/mod/<str:folder>/<str:filename>", static_protected_moderator_js, name="protectedModerator"),
    path("protected/static/man/<str:folder>/<str:filename>", static_protected_manager_js, name="protectedManager"),
    
    
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