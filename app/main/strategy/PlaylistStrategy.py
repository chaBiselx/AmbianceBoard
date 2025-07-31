"""
Fabrique de stratégies pour la gestion des différents types de playlists.

Implémente le pattern Strategy pour gérer les différents comportements
selon le type de playlist (Instant, Ambient, Music).
"""

from typing import Dict, Type
from .playlistConfig.AbstractConfig import AbstractConfig
from .playlistConfig.ConfigInstant import ConfigInstant
from .playlistConfig.ConfigAmbient import ConfigAmbient
from .playlistConfig.ConfigMusic import ConfigMusic
from main.enum.PlaylistTypeEnum import PlaylistTypeEnum

class PlaylistStrategy:
    """
    Fabrique de stratégies pour la gestion des playlists.
    
    Implémente le pattern Strategy pour retourner la stratégie appropriée
    selon le type de playlist. Chaque type de playlist a ses propres
    règles de validation, d'affichage et de traitement.
    """
    
    _strategies: Dict[str, AbstractConfig] = {
        PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name: ConfigInstant(),
        PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name: ConfigAmbient(),
        PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name: ConfigMusic(),
    }
    
    def get_strategy(self, config_type: str) -> AbstractConfig:
        """
        Retourne la stratégie appropriée selon le type de configuration.
        
        Args:
            config_type (str): Type de playlist (INSTANT, AMBIENT, MUSIC)
            
        Returns:
            AbstractConfig: Stratégie correspondante ou ConfigInstant par défaut
        """
        return self._strategies.get(
            config_type,
            ConfigInstant()  # Une stratégie par défaut si le type est inconnu
        )