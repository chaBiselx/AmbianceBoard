from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.views.generic.base import TemplateView
from django.conf.urls.static import static

from main.views.generalViews import home, pricing,  create_account, login_view, logout_view, resend_email_confirmation, send_reset_password, token_validation_reset_password, legal_notice,  dismiss_general_notification
from main.views.privateSoundboardViews import soundboard_list, soundboard_organize, soundboard_organize_update
from main.views.privateSoundboardFromViews import soundboard_create, soundboard_update, soundboard_delete
from main.views.privateShowSoundboardViews import playlist_show, music_stream, update_direct_volume
from main.views.privatePlaylistFormViews import playlist_read_all, playlist_create, playlist_create_with_soundboard, playlist_update, playlist_describe_type, playlist_listing_colors, playlist_create_track_stream, playlist_delete
from main.views.privatePlaylistFormTrackViews import music_create, music_update, music_delete, upload_multiple_music
from main.views.privatePlaylistFormTrackViews import link_create, link_update, link_delete
from main.views.moderatorViews import moderator_dashboard, moderator_listing_images_playlist, moderator_listing_images_soundboard, moderator_get_infos_playlist, moderator_get_infos_soundboard, moderator_listing_log_moderation, moderator_get_infos_user, moderator_listing_report, moderator_listing_report_archived, moderator_get_infos_report, reporting_add_log, moderator_listing_tags, moderator_create_tag, moderator_edit_tag, moderator_get_infos_tag
from main.views.managerUserTierViews import admin_user_tiers_dashboard, admin_user_tiers_listing, manager_user_tier_edit, manager_user_tier_bulk_action, manager_user_tiers_expiring
from main.views.settingsViews import settings_index, settings_update_default_style, update_theme , update_playlist_dim, update_soundboard_dim, update_dimensions, delete_account
from main.views.managerViews import manager_dashboard, user_activity_dashboard
from main.views.managerCronViews import listing_cron_views, clean_media_folder, expire_account, sync_domain_blacklist, purge_expired_shared_soundboard
from main.views.publicViews import public_index, public_listing_soundboard, public_soundboard_read_playlist, public_music_stream, public_stop_stream, favorite_update, reporting_content, public_favorite
from main.views.sharedViews import publish_soundboard, shared_soundboard_read, shared_music_stream
from main.views.confirmViews import confirm_account
from main.channels.SharedSoundboard import SharedSoundboard


urlpatterns = [
    #SEO 
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots_txt"),
    path("sitemap.xml", TemplateView.as_view(template_name="sitemap.xml", content_type="application/xml"), name="sitemap_xml"),

    # Pages publiques
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("legal-notice", legal_notice, name="legalNotice"),
    path("pricing", pricing, name="pricing"),


    # Pages d'authentification
    path("create-account/", create_account, name="createAccount"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("resend-email/", resend_email_confirmation, name="resend_email_confirmation"),
    path("resend-email/confirm/<uuid:uuid_user>/<uuid:confirmation_token>", confirm_account, name="confirm_account"),
    path("reset-password", send_reset_password, name="send_reset_password"),
    path("reset-password/validate/<uuid:uuid_user>/<str:token_reinitialisation>", token_validation_reset_password, name="token_validation_reset_password"),

    path("notification/dismiss/<uuid:notification_uuid>/", dismiss_general_notification, name="dismissGeneralNotification"),

    path("soundBoards/", soundboard_list, name="soundboardsList"),
    path("soundBoards/new", soundboard_create, name="soundboardsNew"),
    path("soundBoards/<uuid:soundboard_uuid>", playlist_show, name="soundboardsRead"),
    path("soundBoards/<uuid:soundboard_uuid>/update", soundboard_update, name="soundboardsUpdate"),
    path("soundBoards/<uuid:soundboard_uuid>/delete", soundboard_delete, name="soundboardsDelete"),
    path("soundBoards/<uuid:soundboard_uuid>/organize", soundboard_organize, name="organizeSoundboard"),
    path("soundBoards/<uuid:soundboard_uuid>/organize/update", soundboard_organize_update, name="organizeSoundboardUpdate"),
    path("soundBoards/<uuid:soundboard_uuid>/user/favorite", favorite_update, name="publicFavoriteSoundboard"),
    
    
    path('account/settings/',settings_index, name="settingsIndex"),
    path('account/settings/theme',update_theme, name="updateTheme"),
    path('account/settings/dimensions',update_dimensions, name="updateDimensions"),
    path('account/settings/playlists/style',settings_update_default_style, name="defaultPlaylistType"),
    path('account/settings/playlists/dimension',update_playlist_dim, name="updatePlaylistDim"),
    path('account/settings/soundboards/dimension',update_soundboard_dim, name="updateSoundboardDim"),
    path('account/settings/delete-account',delete_account, name="deleteAccount"),

    path("soundBoards/<uuid:soundboard_uuid>/music/create", playlist_create_with_soundboard, name="addPlaylistWithSoundboard"),
    path("playlist/create", playlist_create, name="addPlaylist"),
    path("playlist/all", playlist_read_all, name="playlistsAllList"),
    path("playlist/<uuid:playlist_uuid>/update", playlist_update, name="playlistUpdate"),
    path("playlist/<uuid:playlist_uuid>/delete", playlist_delete, name="playlistDelete"),
    path("playlist/<uuid:playlist_uuid>/<int:music_id>", playlist_create_track_stream, name="playlistCreateTrackStream"),
    path("playlist/type/describe", playlist_describe_type, name="playlistDescribeType"),
    
    path("playlist/<uuid:playlist_uuid>/music/create", music_create, name="addMusic"),
    path("playlist/<uuid:playlist_uuid>/music/upload-multiple", upload_multiple_music, name="uploadMultipleMusic"),
    path("playlist/<uuid:playlist_uuid>/music/edit/<int:music_id>", music_update, name="editMusic"),
    path("playlist/<uuid:playlist_uuid>/music/delete/<int:music_id>", music_delete, name="deleteMusic"),
    
    path("playlist/<uuid:playlist_uuid>/link/create", link_create, name="addLink"),
    path("playlist/<uuid:playlist_uuid>/link/edit/<int:link_id>", link_update, name="editLink"),
    path("playlist/<uuid:playlist_uuid>/link/delete/<int:link_id>", link_delete, name="deleteLink"),

    path("playlist/<uuid:soundboard_uuid>/<uuid:playlist_uuid>/stream", music_stream, name="streamMusic"),
    
    path("playlist/<uuid:playlist_uuid>/volume/update", update_direct_volume, name="update_direct_volume"),
    
    path("playlist/other-colors", playlist_listing_colors, name="getListingOtherColors"),
    
    path("public/", public_index, name="publicIndex"),
    path("public/soundboards", public_listing_soundboard, name="publicListingSoundboard"),
    path("public/soundboards/<uuid:soundboard_uuid>", public_soundboard_read_playlist, name="publicReadSoundboard"),
    path("public/soundboards/<uuid:soundboard_uuid>/<uuid:playlist_uuid>/stream", public_music_stream, name="publicStreamMusic"),
    path("public/soundboards/<uuid:soundboard_uuid>/<uuid:playlist_uuid>/stream/stop", public_stop_stream, name="publicStopStreamMusic"),
    path("public/report", reporting_content, name="publicReportingContent"),
    path("public/favorite", public_favorite, name="publicFavorite"),
    
    path('shared/<uuid:soundboard_uuid>', publish_soundboard, name="publish_soundboard"),
    path('shared/<uuid:soundboard_uuid>/<str:token>', shared_soundboard_read, name="shared_soundboard"),
    path('shared/<uuid:soundboard_uuid>/<str:token>/<uuid:playlist_uuid>/<int:music_id>/stream', shared_music_stream, name="sharedStreamMusic"),
    
    
    
    path("moderator/", moderator_dashboard, name="moderatorDashboard"),
    path("moderator/playlist/", moderator_listing_images_playlist, name="moderatorControleImagesPlaylist"),
    path("moderator/playlist/<uuid:playlist_uuid>", moderator_get_infos_playlist, name="moderatorGetDataPlaylist"),
    path("moderator/soundboard", moderator_listing_images_soundboard, name="moderatorControleImagesSoundboard"),
    path("moderator/soundboard/<uuid:soundboard_uuid>", moderator_get_infos_soundboard, name="moderatorGetDataSoundboard"),
    path("moderator/report/content", moderator_listing_report, name="moderatorControleReport"),
    path("moderator/report/content/archive", moderator_listing_report_archived, name="moderatorControleReportArchived"),
    path("moderator/report/content/<int:report_id>", moderator_get_infos_report, name="moderatorGetDataContentReport"),
    path("moderator/log/", moderator_listing_log_moderation, name="moderatorControleLog"),
    path("moderator/log/user/<uuid:user_uuid>", moderator_get_infos_user, name="moderatorGetDataUser"),
    path("moderator/log/add/", reporting_add_log, name="moderatorAddLog"),
    
    path("moderator/tags/", moderator_listing_tags, name="moderatorListingTags"),
    path("moderator/tags/create/", moderator_create_tag, name="moderatorCreateTag"),
    path("moderator/tags/<uuid:tag_uuid>/", moderator_get_infos_tag, name="moderatorGetInfosTag"),
    path("moderator/tags/<uuid:tag_uuid>/edit/", moderator_edit_tag, name="moderatorEditTag"),
    
    
    path("manager/", manager_dashboard, name="managerDashboard"),
    path("manager/cron/", listing_cron_views, name="managerCronViews"),
    path("manager/cron/clean-media-folders", clean_media_folder, name="adminCleanMediaFolders"),
    path("manager/cron/user-tiers", expire_account, name="managerExpireUserTiers"),
    path("manager/cron/sync-domain-blacklist", sync_domain_blacklist, name="managerSyncDomainBlacklist"),
    path("manager/cron/purge-expired-shared-soundboard", purge_expired_shared_soundboard, name="managerPurgeExpiredSharedSoundboard"),

    path("manager/dashboard/user-activity/", user_activity_dashboard, name="managerUserActivityDashboard"),


    # Administration des tiers d'utilisateurs
    path("manager/user-tiers/", admin_user_tiers_dashboard, name="adminUserTiersDashboard"),
    path("manager/user-tiers/listing/", admin_user_tiers_listing, name="adminUserTiersListing"),
    path("manager/user-tiers/<uuid:user_uuid>/edit/", manager_user_tier_edit, name="adminUserTierEdit"),
    path("manager/user-tiers/bulk-action/", manager_user_tier_bulk_action, name="managerUserTierBulkAction"),
    path("manager/user-tiers/expiring/", manager_user_tiers_expiring, name="managerUserTiersExpiring"),
    
    
    path('shared/ws/<uuid:soundboard_uuid>/<str:token>', SharedSoundboard.as_asgi(), name='soundboard_ws'),
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