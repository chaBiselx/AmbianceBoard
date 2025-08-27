from typing import Any
from django.db import models
from main.architecture.persistence.models.User import User
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.utils.cache.CacheFactory import CacheFactory


class PlaylistColorUser(models.Model):
    """
    Modèle représentant les couleurs par défaut des playlists pour un utilisateur.
    
    Permet à chaque utilisateur de définir des couleurs personnalisées
    pour chaque type de playlist (instantané, ambiance, musique).
    Gère automatiquement le cache pour optimiser les performances.
    """
    
    id = models.AutoField(primary_key=True, auto_created=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    typePlaylist = models.CharField(max_length=64, choices=[
        (PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name, 'Son instantanné'),
        (PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name, 'Son d\'ambiance'),
        (PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name, 'Musique'),
    ])
    color = models.CharField(default="#000000",max_length=7)  # Format hexa (ex: #FFFFFF)
    colorText = models.CharField(default="#ffffff",max_length=7)  # Format hexa (ex: #FFFFFF)
    
    
    class Meta:
        unique_together = ('user', 'typePlaylist')
        
    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Sauvegarde les couleurs de playlist avec nettoyage du cache.
        
        Args:
            *args: Arguments positionnels pour la méthode save
            **kwargs: Arguments nommés pour la méthode save
        """
        super().save(*args, **kwargs)
        # clear cache
        self.clear_color_cache()
        
    def delete(self, *args: Any, **kwargs: Any) -> None:
        """
        Supprime les couleurs de playlist avec nettoyage du cache.
        
        Args:
            *args: Arguments positionnels pour la méthode delete
            **kwargs: Arguments nommés pour la méthode delete
        """
        self.clear_color_cache()
        super().delete(*args, **kwargs)

    def __str__(self) -> str:
        """
        Représentation textuelle des couleurs de playlist utilisateur.
        
        Returns:
            str: Utilisateur et type de playlist
        """
        return f"{self.user} ({self.typePlaylist}) "
    
    def clear_color_cache(self) -> None:
        """
        Supprime le cache lié à la couleur de cette playlist pour l'utilisateur.
        
        Cette méthode est appelée automatiquement lors de la sauvegarde
        ou suppression pour maintenir la cohérence du cache.
        """
        if self.user_id and self.typePlaylist:
            cache = CacheFactory.get_default_cache()
            cache_key = f"default_color:{self.user_id}:{self.typePlaylist}"
            cache.delete(cache_key)
        
   