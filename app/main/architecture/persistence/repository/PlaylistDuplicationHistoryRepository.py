from typing import Optional
from django.db.models import QuerySet
from main.architecture.persistence.models.PlaylistDuplicationHistory import PlaylistDuplicationHistory
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User


class PlaylistDuplicationHistoryRepository:
    """
    Repository pour gérer les opérations de base de données 
    liées à l'historique de duplication de playlists.
    """
    
    def create(
        self,
        source_playlist: Playlist,
        duplicated_playlist: Playlist,
        source_playlist_name: str,
        source_playlist_uuid: str
    ) -> PlaylistDuplicationHistory:
        """
        Crée un nouvel enregistrement d'historique de duplication.
        
        Args:
            source_playlist: La playlist source
            duplicated_playlist: La playlist dupliquée
            source_playlist_name: Nom de la playlist source
            source_playlist_uuid: UUID de la playlist source
            
        Returns:
            PlaylistDuplicationHistory: L'enregistrement créé
        """
        history = PlaylistDuplicationHistory(
            source_playlist=source_playlist,
            duplicated_playlist=duplicated_playlist,
            source_playlist_name=source_playlist_name,
            source_playlist_uuid=source_playlist_uuid,
        )
        history.save()
        return history
    
    def find_existing_duplication(
        self,
        source_playlist_uuid: str,
        target_user: User
    ) -> Optional[PlaylistDuplicationHistory]:
        """
        Recherche une duplication existante pour une playlist source 
        et un utilisateur cible.
        
        Args:
            source_playlist_uuid: UUID de la playlist source
            target_user: L'utilisateur qui aurait dupliqué la playlist
            
        Returns:
            Optional[PlaylistDuplicationHistory]: L'historique trouvé ou None
        """
        return PlaylistDuplicationHistory.objects.filter(
            source_playlist_uuid=source_playlist_uuid,
            duplicated_playlist__user=target_user
        ).first()
    
    def get_duplications_by_source(
        self,
        source_playlist_uuid: str
    ) -> QuerySet[PlaylistDuplicationHistory]:
        """
        Récupère toutes les duplications d'une playlist source.
        
        Args:
            source_playlist_uuid: UUID de la playlist source
            
        Returns:
            QuerySet: Liste des duplications
        """
        return PlaylistDuplicationHistory.objects.filter(
            source_playlist_uuid=source_playlist_uuid
        ).select_related('duplicated_playlist', 'duplicated_playlist__user')
    
    def get_duplications_by_user(
        self,
        user: User
    ) -> QuerySet[PlaylistDuplicationHistory]:
        """
        Récupère toutes les duplications effectuées par un utilisateur.
        
        Args:
            user: L'utilisateur
            
        Returns:
            QuerySet: Liste des duplications de l'utilisateur
        """
        return PlaylistDuplicationHistory.objects.filter(
            duplicated_playlist__user=user
        ).select_related('source_playlist', 'duplicated_playlist')
    
    def count_duplications_by_source(
        self,
        source_playlist_uuid: str
    ) -> int:
        """
        Compte le nombre de fois qu'une playlist a été dupliquée.
        
        Args:
            source_playlist_uuid: UUID de la playlist source
            
        Returns:
            int: Nombre de duplications
        """
        return PlaylistDuplicationHistory.objects.filter(
            source_playlist_uuid=source_playlist_uuid
        ).count()
