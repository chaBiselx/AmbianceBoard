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
    SOUNDBOARD_VIEW = "soundboard_view"
    SOUNDBOARD_SHARE = "soundboard_share"
    
    # Actions sur les playlists
    PLAYLIST_CREATE = "playlist_create"
    PLAYLIST_VIEW = "playlist_view"
    PLAYLIST_PLAY = "playlist_play"
    
    # Actions sur les musiques
    MUSIC_UPLOAD = "music_upload"
    MUSIC_DELETE = "music_delete"
    
    # Actions de modération
    REPORT_CONTENT = "report_content"
    
    # Actions d'erreur
    ERROR_404 = "error_404"
    ERROR_500 = "error_500"
    ERROR_PERMISSION = "error_permission"
