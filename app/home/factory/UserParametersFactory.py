

from parameters import settings
from home.models.User import User
from home.enum.PermissionEnum import PermissionEnum
from home.utils.UserTierManager import UserTierManager

class UserParametersFactory:
    def __init__(self, user: User): 
        self._user = user
        
        # Récupération des limites basées sur le nouveau système de tiers
        user_limits = UserTierManager.get_user_limits(user)
        
        # Application des limites avec possibilité de surcharge premium
        self.limit_soundboard = user_limits['soundboard']
        self.limit_playlist = user_limits['playlist']
        self.limit_music_per_playlist = user_limits['music_per_playlist']
        self.limit_weight_file = user_limits['weight_music_mb']
        

    @property
    def user_tier_name(self):
        """Retourne le nom du tier de l'utilisateur"""
        return self._user.tier_info.tier_name
    
    @property
    def user_tier_display_name(self):
        """Retourne le nom d'affichage du tier de l'utilisateur"""
        return UserTierManager.get_tier_display_name(self.user_tier_name)
