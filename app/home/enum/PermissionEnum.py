from enum import Enum

class PermissionEnum(Enum): 
    USER_STANDARD = "user_standard"
    MODERATEUR_ACCESS_ALL_MUSIC = "moderateur_access_all_music"
    MODERATEUR_ACCESS_ALL_PLAYLIST = "moderateur_access_all_playlist"
    MODERATEUR_ACCESS_ALL_SOUNDBOARD = "moderateur_access_all_soundboard"
    MODERATEUR_ACCESS_DASHBOARD = "moderateur_access_dashboard"
    MANAGER_ATTRIBUTE_MODERATEUR_ROLE = "manager_attribute_moderateur_role"
    MANAGER_ACCESS_DASHBOARD = "manager_access_dashboard"
    MANAGER_EXECUTE_BATCHS = "manager_execute_batchs"
    
    