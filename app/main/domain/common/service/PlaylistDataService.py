"""
Service pour récupérer les données de configuration d'une playlist.

Ce service est responsable de la récupération des données spécifiques
à chaque type de playlist en utilisant le pattern Strategy.
"""

from typing import Any, Dict
from main.domain.common.strategy.PlaylistStrategy import PlaylistStrategy
from main.domain.common.enum.FadePlaylistEnum import FadePlaylistEnum


class PlaylistDataService:
    """
    Service de récupération des données de playlist.
    
    Utilise le pattern Strategy pour obtenir les données appropriées
    selon le type de playlist (musique, ambiant, instantané).
    """
    
    def __init__(self):
        """Initialise le service avec la fabrique de stratégies."""
        self.strategy_factory = PlaylistStrategy()
    
    def get_playlist_data(self, playlist: Any) -> Dict[str, Any]:
        """
        Récupère les données de configuration de la playlist selon son type.
        
        Applique les surcharges de fadeIn/fadeOut si elles sont définies
        sur la playlist (YES ou NO), sinon utilise les valeurs par défaut
        de la stratégie.
        
        Args:
            playlist: Instance du modèle Playlist
            
        Returns:
            Dict[str, Any]: Dictionnaire contenant les données de configuration
                          de la playlist (volume, fade, delay, etc.)
        """
        strategy = self.strategy_factory.get_strategy(playlist.typePlaylist)
        data = strategy.get_data(playlist)
        
        data = self._apply_fade_override(data, playlist, 'fadeIn')
        data = self._apply_fade_override(data, playlist, 'fadeOut')
        
        return data
    
    def _apply_fade_override(self, data: Dict[str, Any], playlist: Any, fade_type: str) -> Dict[str, Any]:
        """
        Applique la surcharge de configuration fade (fadeIn ou fadeOut).
        
        Si la playlist a une configuration spécifique (YES ou NO), 
        elle remplace la valeur par défaut de la stratégie.
        DEFAULT conserve la valeur de la stratégie.
        
        Args:
            data: Dictionnaire de données actuel
            playlist: Instance du modèle Playlist
            fade_type: Type de fade ('fadeIn' ou 'fadeOut')
            
        Returns:
            Dict[str, Any]: Dictionnaire avec la surcharge appliquée
        """
        fade_value = getattr(playlist, fade_type, FadePlaylistEnum.DEFAULT.name)
        
        if fade_value == FadePlaylistEnum.YES.name:
            # Active explicitement le fade
            data[fade_type] = True
        elif fade_value == FadePlaylistEnum.NO.name:
            # Désactive explicitement le fade
            data[fade_type] = False
            # Si désactivé, on met les durées à 0
            data[f"{fade_type}Duration"] = 0
        # Si DEFAULT, on garde les valeurs de la stratégie (pas de modification)
        
        return data
