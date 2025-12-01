from typing import Any
import uuid
from django.db import models
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.Playlist import Playlist


class PlaylistDuplicationHistory(models.Model):
    """
    Modèle représentant l'historique des duplications de playlists.
    
    Permet de tracer qui a dupliqué quelle playlist, quand et à partir de quelle playlist source.
    Utile pour suivre la popularité des playlists partagées et l'activité de duplication.
    """
    
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Playlist source (celle qui a été copiée)
    source_playlist = models.ForeignKey(
        Playlist, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='duplication_sources',
        help_text="La playlist originale qui a été dupliquée"
    )
    # Playlist dupliquée (la copie créée)
    duplicated_playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name='duplication_history',
        help_text="La playlist dupliquée (copie)"
    )
    
    # Nom de la playlist source au moment de la duplication (pour garder une trace même si elle est supprimée)
    source_playlist_name = models.CharField(
        max_length=255,
        help_text="Nom de la playlist source au moment de la duplication"
    )
    # UUID de la playlist source (pour garder une trace même si elle est supprimée)
    source_playlist_uuid = models.UUIDField(
        help_text="UUID de la playlist source"
    )
    
    class Meta:
        verbose_name = "Historique de duplication de playlist"
        verbose_name_plural = "Historiques de duplication de playlists"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source_playlist_uuid']),
        ]
    
    def __str__(self) -> str:
        """
        Représentation textuelle de l'historique de duplication.
        
        Returns:
            str: Description de la duplication avec les informations principales
        """
        source_name = self.source_playlist_name or "Playlist supprimée"
        return f"'{source_name}' le {self.created_at.strftime('%d/%m/%Y à %H:%M')} dupliquée en '{self.duplicated_playlist.name}'"
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Sauvegarde l'historique de duplication.
        
        Pré-remplit automatiquement les informations de la playlist source si elles ne sont pas définies.
        
        Args:
            *args: Arguments positionnels pour la méthode save
            **kwargs: Arguments nommés pour la méthode save
        """
        # Si c'est une nouvelle entrée et que les infos source ne sont pas renseignées
        if not self.pk and self.source_playlist:
            if not self.source_playlist_name:
                self.source_playlist_name = self.source_playlist.name
            if not self.source_playlist_uuid:
                self.source_playlist_uuid = self.source_playlist.uuid
        
        super().save(*args, **kwargs)
