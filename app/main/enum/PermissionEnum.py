"""
Énumération des permissions spécifiques.

Définit les permissions granulaires pour contrôler l'accès
aux différentes fonctionnalités de l'application.
"""

from .BaseEnum import BaseEnum

class PermissionEnum(BaseEnum):
    """
    Énumération des permissions spécifiques du système.
    
    Définit les permissions granulaires pour :
    - Utilisateurs standards
    - Modérateurs (accès aux contenus, dashboard)
    - Managers (attribution de rôles, exécution de tâches)
    """
    
    USER_STANDARD = "user_standard"
    MODERATEUR_ACCESS_ALL_MUSIC = "moderateur_access_all_music"
    MODERATEUR_ACCESS_ALL_PLAYLIST = "moderateur_access_all_playlist"
    MODERATEUR_ACCESS_ALL_SOUNDBOARD = "moderateur_access_all_soundboard"
    MODERATEUR_ACCESS_DASHBOARD = "moderateur_access_dashboard"
    MANAGER_ATTRIBUTE_MODERATEUR_ROLE = "manager_attribute_moderateur_role"
    MANAGER_ACCESS_DASHBOARD = "manager_access_dashboard"
    MANAGER_EXECUTE_BATCHS = "manager_execute_batchs"