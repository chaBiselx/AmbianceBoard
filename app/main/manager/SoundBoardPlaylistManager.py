"""
Manager pour la gestion des playlists dans les soundboards.

Fournit des méthodes pour gérer l'association et l'organisation
des playlists au sein d'un soundboard.
"""

from typing import List
from ..models.SoundBoard import SoundBoard
from ..models.Playlist import Playlist
from ..service.PlaylistService import PlaylistService

class SoundBoardPlaylistManager:
    """
    Manager pour la gestion des playlists dans un soundboard.
    
    Fournit des méthodes pour :
    - Récupérer les playlists associées à un soundboard
    - Trouver les playlists non associées disponibles
    - Gérer l'ordre des playlists
    """
    
    def __init__(self, request, soundboard: SoundBoard) -> None:
        """
        Initialise le manager avec le soundboard cible.
        
        Args:
            request: Requête HTTP pour l'accès aux services
            soundboard: Soundboard à gérer
        """
        self.request = request
        self.soundboard = soundboard

    def get_playlists(self) -> List[Playlist]:
        """
        Récupère toutes les playlists associées au soundboard.
        
        Returns:
            List[Playlist]: Liste des playlists ordonnées selon leur position
                           dans le soundboard
        """
        return list(self.soundboard.playlists.all().order_by('soundboardplaylist__order'))

    def get_unassociated_playlists(self) -> List[Playlist]:
        """
        Récupère les playlists de l'utilisateur non associées à ce soundboard.
        
        Returns:
            List[Playlist]: Liste des playlists disponibles pour l'association
        """
        all_playlists = list((PlaylistService(self.request)).get_all_playlist())
        associated_playlists = list(self.soundboard.playlists.all())
        return [playlist for playlist in all_playlists if playlist not in associated_playlists]