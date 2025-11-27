import uuid
from typing import Optional
from django.db import transaction
from django.core.files.base import ContentFile
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.LinkMusic import LinkMusic
from main.architecture.persistence.models.Track import Track
from main.architecture.persistence.repository.PlaylistDuplicationHistoryRepository import PlaylistDuplicationHistoryRepository
from main.domain.common.exceptions.PlaylistDuplicationException import (
    PlaylistAlreadyDuplicatedException,
    PlaylistNotCopiableException
)


class PlaylistDuplicationService:
    """
    Service pour gérer la duplication complète de playlists.
    
    Ce service permet de dupliquer une playlist avec tous ses éléments musicaux
    (Music et LinkMusic) tout en conservant l'historique de duplication.
    Il vérifie qu'un utilisateur ne duplique pas deux fois la même playlist.
    """
    
    def __init__(self, source_playlist: Playlist, target_user: User):
        """
        Initialise le service de duplication.
        
        Args:
            source_playlist: La playlist à dupliquer
            target_user: L'utilisateur qui reçoit la copie
        """
        self.source_playlist = source_playlist
        self.target_user = target_user
        self.duplication_history_repository = PlaylistDuplicationHistoryRepository()
        
    def duplicate(self, new_name: Optional[str] = None) -> Playlist:
        """
        Duplique la playlist avec tous ses éléments musicaux.
        
        Crée une nouvelle playlist avec un nouvel UUID, copie tous les tracks
        (Music et LinkMusic) avec de nouveaux UUID, et enregistre l'historique.
        
        Args:
            new_name: Nom optionnel pour la nouvelle playlist.
                     Si None, utilise le nom original avec "(copie)"
        
        Returns:
            Playlist: La nouvelle playlist dupliquée
            
        Raises:
            PlaylistNotCopiableException: Si la playlist n'est pas marquée comme copiable
            PlaylistAlreadyDuplicatedException: Si l'utilisateur a déjà dupliqué cette playlist
        """
        # Vérification 1: La playlist doit être copiable
        if not self.source_playlist.is_copiable:
            raise PlaylistNotCopiableException(
                str(self.source_playlist.uuid),
                self.source_playlist.name
            )
        
        # Vérification 2: L'utilisateur ne doit pas avoir déjà dupliqué cette playlist
        self._check_already_duplicated()
        
        # Duplication avec transaction atomique
        with transaction.atomic():
            # Créer la nouvelle playlist
            duplicated_playlist = self._duplicate_playlist(new_name)
            
            # Copier tous les tracks
            self._duplicate_tracks(duplicated_playlist)
            
            # Enregistrer l'historique
            self._create_history_record(duplicated_playlist)
            
        return duplicated_playlist
    
    def _check_already_duplicated(self) -> None:
        """
        Vérifie si l'utilisateur a déjà dupliqué cette playlist.
        
        Raises:
            PlaylistAlreadyDuplicatedException: Si une duplication existe déjà
        """
        existing_duplication = self.duplication_history_repository.find_existing_duplication(
            source_playlist_uuid=self.source_playlist.uuid,
            target_user=self.target_user
        )
        
        if existing_duplication:
            raise PlaylistAlreadyDuplicatedException(
                str(self.source_playlist.uuid),
                self.target_user.username,
                existing_duplication.created_at.strftime('%d/%m/%Y à %H:%M')
            )
    
    def _duplicate_playlist(self, new_name: Optional[str]) -> Playlist:
        """
        Crée une copie de la playlist avec un nouvel UUID.
        
        Args:
            new_name: Nom optionnel pour la nouvelle playlist
            
        Returns:
            Playlist: La nouvelle playlist créée
        """
        duplicated_playlist = Playlist(
            uuid=uuid.uuid4(),
            user=self.target_user,
            name=new_name or f"{self.source_playlist.name} (copie)",
            typePlaylist=self.source_playlist.typePlaylist,
            useSpecificColor=self.source_playlist.useSpecificColor,
            color=self.source_playlist.color,
            colorText=self.source_playlist.colorText,
            volume=self.source_playlist.volume,
            is_copiable=False,  # La copie n'est pas copiable par défaut
            useSpecificDelay=self.source_playlist.useSpecificDelay,
            maxDelay=self.source_playlist.maxDelay,
            fadeIn=self.source_playlist.fadeIn,
            fadeOut=self.source_playlist.fadeOut,
        )
        
        # Copier l'icône si elle existe
        if self.source_playlist.icon:
            duplicated_playlist.icon.save(
                f"{duplicated_playlist.uuid}.{self.source_playlist.icon.name.split('.')[-1]}",
                ContentFile(self.source_playlist.icon.read()),
                save=False
            )
        
        duplicated_playlist.save()
        return duplicated_playlist
    
    def _duplicate_tracks(self, duplicated_playlist: Playlist) -> None:
        """
        Copie tous les tracks (Music et LinkMusic) vers la nouvelle playlist.
        
        Args:
            duplicated_playlist: La playlist destination
        """
        source_tracks = Track.objects.filter(
            playlist=self.source_playlist
        ).select_related('music', 'linkmusic').order_by('id')
        
        for source_track in source_tracks:
            if source_track.is_music():
                self._duplicate_music(source_track.music, duplicated_playlist)
            elif source_track.is_link_music():
                self._duplicate_link_music(source_track.linkmusic, duplicated_playlist)
    
    def _duplicate_music(self, source_music: Music, duplicated_playlist: Playlist) -> Music:
        """
        Crée une copie d'un fichier Music avec un nouvel UUID.
        
        Args:
            source_music: Le fichier Music source
            duplicated_playlist: La playlist destination
            
        Returns:
            Music: Le nouveau fichier Music créé
        """
        duplicated_music = Music(
            playlist=duplicated_playlist,
            alternativeName=source_music.alternativeName,
            duration=source_music.duration,
            fileName=source_music.fileName,
        )
        
        # Copier le fichier avec un nouveau nom UUID
        if source_music.file:
            new_uuid = uuid.uuid4()
            file_extension = source_music.file.name.split('.')[-1]
            duplicated_music.file.save(
                f"{new_uuid}.{file_extension}",
                ContentFile(source_music.file.read()),
                save=False
            )
        
        duplicated_music.save()
        return duplicated_music
    
    def _duplicate_link_music(self, source_link: LinkMusic, duplicated_playlist: Playlist) -> LinkMusic:
        """
        Crée une copie d'un LinkMusic.
        
        Args:
            source_link: Le LinkMusic source
            duplicated_playlist: La playlist destination
            
        Returns:
            LinkMusic: Le nouveau LinkMusic créé
        """
        duplicated_link = LinkMusic(
            playlist=duplicated_playlist,
            alternativeName=source_link.alternativeName,
            duration=source_link.duration,
            url=source_link.url,
            domained_name=source_link.domained_name,
            urlType=source_link.urlType,
        )
        duplicated_link.save()
        return duplicated_link
    
    def _create_history_record(self, duplicated_playlist: Playlist):
        """
        Enregistre l'historique de duplication.
        
        Args:
            duplicated_playlist: La playlist dupliquée
            
        Returns:
            PlaylistDuplicationHistory: L'enregistrement d'historique créé
        """
        return self.duplication_history_repository.create(
            source_playlist=self.source_playlist,
            duplicated_playlist=duplicated_playlist,
            source_playlist_name=self.source_playlist.name,
            source_playlist_uuid=self.source_playlist.uuid,
        )
