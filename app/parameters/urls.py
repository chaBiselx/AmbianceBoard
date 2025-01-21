from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from home.views.general.views import home, create_account, login_view, logout_view
from home.views.soundboard.views import soundboard_list, soundboard_create, soundboard_read, soundboard_update, soundboard_delete, soundboard_organize, soundboard_organize_update
from home.views.soundboard.views import playlist_create, playlist_read_all, playlist_create_with_soundboard, playlist_update, playlist_delete
from home.views.soundboard.views import music_create, music_update, music_delete,music_stream
from home.views.moderator.views import moderator_dashboard, moderator_listing_images_playlist, moderator_listing_images_soundboard
from home.views.manager.views import manager_dashboard, clean_media_folder

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    
    path("create-account/", create_account, name="createAccount"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    
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
    
    path("moderator/", moderator_dashboard, name="moderatorDashboard"),
    path("moderator/playlist/images", moderator_listing_images_playlist, name="moderatorControleImagesPlaylist"),
    path("moderator/soundboard/images", moderator_listing_images_soundboard, name="moderatorControleImagesSoundboard"),
    
    path("manager/", manager_dashboard, name="managerDashboard"),
    path("manager/clean-media-folders", clean_media_folder, name="adminCleanMediaFolders"),
    
]


if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
