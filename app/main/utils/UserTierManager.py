"""
Gestionnaire des tiers d'utilisateurs
Centralise la logique de gestion des différents niveaux d'utilisateurs
"""

from django.conf import settings
from typing import Dict, Any, Optional
from main.domain.common.enum.GroupEnum import GroupEnum


class UserTierManager:
    """Gestionnaire centralisé pour les tiers d'utilisateurs"""
    
    @staticmethod
    def get_all_tiers() -> Dict[str, Any]:
        """Retourne tous les tiers disponibles"""
        return settings.USER_TIERS
    
    @staticmethod
    def get_tier_info(tier_name: str) -> Optional[Dict[str, Any]]:
        """Retourne les informations complètes d'un tier"""
        return settings.USER_TIERS.get(tier_name)
    
    @staticmethod
    def get_tier_limits(tier_name: str) -> Dict[str, int]:
        """Retourne les limites d'un tier"""
        tier_info = UserTierManager.get_tier_info(tier_name)
        return tier_info['limits'] if tier_info else settings.USER_TIERS['STANDARD']['limits']
    
    @staticmethod
    def get_tier_display_name(tier_name: str) -> str:
        """Retourne le nom d'affichage d'un tier"""
        tier_info = UserTierManager.get_tier_info(tier_name)
        return tier_info['display_name'] if tier_info else 'Utilisateur Standard'
    
    
    @staticmethod
    def get_user_limits(user) -> Dict[str, int]:
        """Retourne les limites applicables à un utilisateur"""
        if not hasattr(user, 'tier_info') or not user.tier_info:
            return UserTierManager.get_tier_limits('STANDARD')
        return UserTierManager.get_tier_limits(user.tier_info.tier_name)
    
    @staticmethod
    def can_user_create_soundboard(user, current_count: int) -> bool:
        """Vérifie si l'utilisateur peut créer un nouveau soundboard"""
        limits = UserTierManager.get_user_limits(user)
        return current_count < limits['soundboard']
    
    @staticmethod
    def can_user_create_playlist(user, current_count: int) -> bool:
        """Vérifie si l'utilisateur peut créer une nouvelle playlist"""
        limits = UserTierManager.get_user_limits(user)
        return current_count < limits['playlist']
    
    @staticmethod
    def can_user_add_music_to_playlist(user, current_count: int) -> bool:
        """Vérifie si l'utilisateur peut ajouter de la musique à une playlist"""
        limits = UserTierManager.get_user_limits(user)
        return current_count < limits['music_per_playlist']
    
    @staticmethod
    def can_user_upload_music_size(user, file_size_mb: float) -> bool:
        """Vérifie si l'utilisateur peut uploader un fichier de cette taille"""
        limits = UserTierManager.get_user_limits(user)
        return file_size_mb <= limits['weight_music_mb']
    
    @staticmethod
    def can_user_share_soundboard(user) -> bool:
        """Vérifie si l'utilisateur peut partager un soundboard"""
        limits = UserTierManager.get_user_limits(user)
        return limits.get('share_soundboard', False)
    
    @staticmethod
    def get_tier_comparison() -> Dict[str, Dict[str, Any]]:
        """Retourne une comparaison de tous les tiers pour l'affichage"""
        comparison = {}
        for tier_name, tier_info in settings.USER_TIERS.items():
            comparison[tier_name] = {
                'display_name': tier_info['display_name'],
                'limits': tier_info['limits'],
            }
        return comparison
