"""
Énumération pour les types d'activité utilisateur.

Définit les différents types d'actions que peuvent effectuer les utilisateurs
et qui peuvent être tracées à des fins statistiques.
"""

from main.domain.common.enum.BaseEnum import BaseEnum


class UserActivityTypeEnum(BaseEnum):
    """
    Énumération des types d'activité utilisateur traçables.
    
    Cette énumération définit tous les types d'actions que les utilisateurs
    peuvent effectuer dans l'application et qui méritent d'être tracées
    pour des analyses statistiques.
    """
    
    # Actions d'authentification
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTRATION = "registration"
    
    # Actions sur les soundboards
    SOUNDBOARD_CREATE = "soundboard_create"
    SOUNDBOARD_VIEW = "soundboard_view"
    SOUNDBOARD_SHARE = "soundboard_share"
    SOUNDBOARD_DELETE = "soundboard_delete"

    # Actions sur les playlists
    PLAYLIST_CREATE = "playlist_create"
    PLAYLIST_DELETE = "playlist_delete"

    # Actions sur les musiques
    MUSIC_UPLOAD = "music_upload"
    MUSIC_DELETE = "music_delete"
    LINK_UPLOAD = "link_upload"
    LINK_DELETE = "link_delete"

    # Actions de modération
    REPORT_CONTENT = "report_content"
    
    # Actions d'erreur
    ERROR_404 = "error_404"
    ERROR_405 = "error_405"
    ERROR_406 = "error_406"
    ERROR_429 = "error_429"
    ERROR_4XX = "error_4xx"
    ERROR_500 = "error_500"
    ERROR_5XX = "error_5xx"

    @classmethod
    def listing_errors(cls):
        return {
            "404": cls.ERROR_404, 
            "405": cls.ERROR_405, 
            "406": cls.ERROR_406, 
            "429": cls.ERROR_429, 
            "500": cls.ERROR_500,
            "4XX": cls.ERROR_4XX,
            "5XX": cls.ERROR_5XX
        }
        
    @classmethod
    def listing_reporting_errors(cls):
        return {
            "error_404": cls.ERROR_404, 
            "error_405": cls.ERROR_405, 
            "error_406": cls.ERROR_406, 
            "error_429": cls.ERROR_429, 
            "error_500": cls.ERROR_500,
            "error_4XX": cls.ERROR_4XX,
            "error_5XX": cls.ERROR_5XX
        }
        
    @classmethod
    def listing_reporting_activities(cls):
        return {
            "login": cls.LOGIN,
            "logout": cls.LOGOUT,
            "registration": cls.REGISTRATION,
            "soundboard_create": cls.SOUNDBOARD_CREATE,
            "soundboard_view": cls.SOUNDBOARD_VIEW,
            "soundboard_share": cls.SOUNDBOARD_SHARE,
            "soundboard_delete": cls.SOUNDBOARD_DELETE,
            "playlist_create": cls.PLAYLIST_CREATE,
            "playlist_delete": cls.PLAYLIST_DELETE,
            "music_upload": cls.MUSIC_UPLOAD,
            "music_delete": cls.MUSIC_DELETE,
            "link_upload": cls.LINK_UPLOAD,
            "link_delete": cls.LINK_DELETE,
            "report_content": cls.REPORT_CONTENT
        }

