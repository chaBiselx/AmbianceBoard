"""
Énumération pour les types d'activité utilisateur.

Définit les différents types d'actions que peuvent effectuer les utilisateurs
et qui peuvent être tracées à des fins statistiques.
"""

from main.enum.BaseEnum import BaseEnum


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
    SOUNDBOARD_VIEW = "soundboard_view" #TODO
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
    ERROR_404 = "error_404" #TODO
    ERROR_500 = "error_500" #TODO
    ERROR_PERMISSION = "error_permission" #TODO
