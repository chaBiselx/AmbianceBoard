"""
Factory pour la gestion des paramètres et limites utilisateur.

Centralise la logique de détermination des limites et permissions
basées sur le tier de l'utilisateur.
"""

from typing import Dict, Any
from parameters import settings
from main.architecture.persistence.models.User import User
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.utils.UserTierManager import UserTierManager

class UserParametersFactory:
    """
    Factory pour la gestion des paramètres utilisateur.
    
    Détermine les limites et permissions d'un utilisateur
    basées sur son tier (STANDARD, PREMIUM, etc.) et applique
    les règles métier appropriées.
    """
    
    def __init__(self, user: User) -> None:
        """
        Initialise la factory avec un utilisateur.
        
        Calcule automatiquement toutes les limites basées sur le tier
        de l'utilisateur via le UserTierManager.
        
        Args:
            user: Utilisateur pour lequel calculer les paramètres
        """
        self._user = user
        
        # Récupération des limites basées sur le nouveau système de tiers
        user_limits = UserTierManager.get_user_limits(user)
        
        # Application des limites avec possibilité de surcharge premium
        self.limit_soundboard = user_limits['soundboard']
        self.limit_playlist = user_limits['playlist']
        self.limit_music_per_playlist = user_limits['music_per_playlist']
        self.limit_weight_file = user_limits['weight_music_mb']

    @property
    def user_tier_name(self) -> str:
        """
        Retourne le nom du tier de l'utilisateur.
        
        Returns:
            str: Nom technique du tier (ex: STANDARD, PREMIUM)
        """
        return self._user.tier_info.tier_name
    
    @property
    def user_tier_display_name(self) -> str:
        """
        Retourne le nom d'affichage du tier de l'utilisateur.
        
        Returns:
            str: Nom d'affichage localisé du tier
        """
        return UserTierManager.get_tier_display_name(self.user_tier_name)
