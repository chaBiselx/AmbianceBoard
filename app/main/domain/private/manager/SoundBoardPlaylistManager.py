"""
Manager pour la gestion des playlists dans les soundboards.

Fournit des méthodes pour gérer l'association et l'organisation
des playlists au sein d'un soundboard.
"""

from typing import List

from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.domain.common.service.PlaylistService import PlaylistService
from main.architecture.persistence.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository

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
        return {
            section.section: playlists
            for section, playlists in self.sound_play_repository.get_sectioned_playlists(
                self.soundboard
            )
        }

    def get_unassociated_playlists(self) -> List[Playlist]:
        """
        Récupère les playlists de l'utilisateur non associées à ce soundboard.

        Les liens sont stockés via SoundboardSection -> SoundboardPlaylist,
        donc on exclut les IDs déjà rattachés à ce soundboard.
        """
        all_playlists = list((PlaylistService(self.request)).get_listing_playlist())
        associated_playlist_ids = set(
            SoundboardPlaylist.objects.filter(section__SoundBoard=self.soundboard)
            .values_list('Playlist_id', flat=True)
        )
        return [
            playlist for playlist in all_playlists
            if playlist.id not in associated_playlist_ids
        ]