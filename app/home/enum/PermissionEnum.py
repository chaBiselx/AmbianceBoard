from enum import Enum

class PermissionEnum(Enum): 
    USER_STANDARD = "user_standard"
    USER_PREMIUM_OVER_LIMIT_SOUNDBOARD = "user_premium_over_limit_soundboard"
    USER_PREMIUM_OVER_LIMIT_PLAYLIST = "user_premium_over_limit_playlist"
    USER_PREMIUM_OVER_LIMIT_WEIGHT_MUSIC = "user_premium_over_limit_weight_music"
    MODERATEUR_ACCESS_ALL_MUSIC = "moderateur_access_all_music"
    MODERATEUR_ACCESS_ALL_PLAYLIST = "moderateur_access_all_playlist"
    MODERATEUR_ACCESS_ALL_SOUNDBOARD = "moderateur_access_all_soundboard"
    MODERATEUR_ACCESS_DASHBOARD = "moderateur_access_dashboard"
    MANAGER_ATTRIBUTE_MODERATEUR_ROLE = "manager_attribute_moderateur_role"
    MANAGER_ACCESS_DASHBOARD = "manager_access_dashboard"
    
    