"""
Manager pour la gestion des playlists dans les soundboards.

Fournit des méthodes pour gérer l'association et l'organisation
des playlists au sein d'un soundboard.
"""

from typing import List
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.Playlist import Playlist
from main.domain.common.service.PlaylistService import PlaylistService
from main.domain.common.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository

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
        self.sound_play_repository = SoundboardPlaylistRepository()

    def get_playlists(self) -> dict:
        """
        Récupère toutes les playlists associées au soundboard.
        
        Returns:
            dict: Dictionnaire des playlists organisées par section {section_number: [playlists]}
        """
        liste_brut = self.sound_play_repository.get_all(self.soundboard)
        tabul = {}
        for playlist_soundboard in liste_brut:
            section = playlist_soundboard.get_section() or 1
            if section not in tabul:
                tabul[section] = []
            tabul[section].append(playlist_soundboard)

        return tabul

    def get_unassociated_playlists(self) -> List[Playlist]:
        """
        Récupère les playlists de l'utilisateur non associées à ce soundboard.
        
        Returns:
            List[Playlist]: Liste des playlists disponibles pour l'association
        """
        all_playlists = list((PlaylistService(self.request)).get_all_playlist())
        associated_playlists = list(self.soundboard.playlists.all())
        return [playlist for playlist in all_playlists if playlist not in associated_playlists]