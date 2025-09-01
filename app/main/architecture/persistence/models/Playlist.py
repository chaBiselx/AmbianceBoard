from typing import Any, Optional
import uuid
from main.domain.common.utils.uuidUtils import is_not_uuid_with_extension
from django.db import models
from django.db.models import QuerySet
from main.architecture.persistence.models.User import User
from django.core.validators import MinValueValidator, MaxValueValidator
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.strategy.PlaylistStrategy import PlaylistStrategy
from main.domain.brokers.message.ReduceSizeImgMessenger import reduce_size_img
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.domain.common.service.DefaultColorPlaylistService import DefaultColorPlaylistService
from main.domain.common.utils.cache.CacheFactory import CacheFactory
from parameters import settings
from main.domain.common.utils.OverwriteStorage import OverwriteStorage


class Playlist(models.Model):
    """
    Modèle représentant une playlist de contenu audio.
    
    Une playlist peut contenir des musiques, des sons d'ambiance ou des sons instantanés.
    Elle peut avoir des couleurs personnalisées, un volume spécifique et des délais configurables.
    """
    
    PLAYLIST_FOLDER = 'playlistIcon/'
    id = models.BigAutoField(primary_key=True,) 
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=255)
    typePlaylist = models.CharField(max_length=64, choices=[
        (PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name, PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.value),
        (PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name, PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.value),
        (PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name, PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.value),
    ])
    useSpecificColor = models.BooleanField(default=False, )
    color = models.CharField(default="#000000",max_length=7)  # Format hexa (ex: #FFFFFF)
    colorText = models.CharField(default="#ffffff",max_length=7)  # Format hexa (ex: #FFFFFF)
    volume = models.IntegerField(default=75, validators=[MinValueValidator(0), MaxValueValidator(100)])
    icon = models.FileField(upload_to=PLAYLIST_FOLDER,storage=OverwriteStorage(), default=None, null=True, blank=True)
    useSpecificDelay = models.BooleanField(default=False, )
    maxDelay = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialise une nouvelle instance de Playlist.
        
        Sauvegarde l'état original de l'icône pour détecter les changements.
        
        Args:
            *args: Arguments positionnels pour le modèle Django
            **kwargs: Arguments nommés pour le modèle Django
        """
        super().__init__(*args, **kwargs)
        self._icon_original = self.icon if self.pk else None
        self.cache = CacheFactory.get_default_cache()

    def __str__(self) -> str:
        """
        Représentation textuelle de la playlist.
        
        Returns:
            str: Nom de la playlist suivi de son UUID entre parenthèses
        """
        return f"{self.name} ({self.uuid}) "


    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Sauvegarde la playlist avec traitement de l'icône.
        
        Vérifie la présence d'un utilisateur, renomme l'icône avec un UUID si nécessaire,
        et lance la tâche de réduction de taille d'image en arrière-plan.
        
        Args:
            *args: Arguments positionnels pour la méthode save
            **kwargs: Arguments nommés pour la méthode save
            
        Raises:
            ValueError: Si la playlist n'a pas d'utilisateur associé
        """
        new_file = False
        if not hasattr(self, 'user') :
            raise ValueError("Playlist must have a user")
            
        if self.icon and (is_not_uuid_with_extension(self.icon.name) or self.__is_new_file()): #Remplacement
            self.__replace_name_by_uuid()
            new_file = True

        if self.useSpecificDelay == False:
            self.maxDelay = 0

        super().save(*args, **kwargs)
        if new_file: 
            reduce_size_img.apply_async(
                args=[self.__class__.__name__, self.pk], 
                queue='default', 
                priority=1 
            )
            
    def update(self, *args: Any, **kwargs: Any) -> None:
        """
        Met à jour la playlist.
        
        Vérifie la présence d'un utilisateur avant de sauvegarder.
        
        Args:
            *args: Arguments positionnels pour la méthode save
            **kwargs: Arguments nommés pour la méthode save
            
        Raises:
            ValueError: Si la playlist n'a pas d'utilisateur associé
        """
        if not hasattr(self, 'user') :
            raise ValueError("Playlist must have a user")
            
        super().save(*args, **kwargs)
    
    def get_data_set(self) -> "QuerySet[Any]":
        """
        Récupère les données de la playlist selon son type.
        
        Utilise le pattern Strategy pour obtenir les données appropriées
        selon le type de playlist (musique, ambiant, instantané).
        
        Returns:
            QuerySet[Any]: QuerySet contenant les données de la playlist
        """
        strategy = PlaylistStrategy().get_strategy(self.typePlaylist)
        return strategy.get_data(self)

    def get_order(self) -> Optional[int]:
        """
        Récupère l'ordre de la playlist dans un soundboard.
        
        Returns:
            Optional[int]: L'ordre de la playlist dans le soundboard,
                          ou None si la playlist n'est dans aucun soundboard
        """
        soundboard_playlist = SoundboardPlaylist.objects.filter(Playlist=self).first()
        return soundboard_playlist.order if soundboard_playlist and soundboard_playlist.order is not None else None
    
    def get_color(self) -> str:
        """
        Récupère la couleur de la playlist.
        
        Utilise la couleur spécifique de la playlist si elle est définie,
        sinon utilise la couleur par défaut de l'utilisateur pour ce type de playlist.
        La réponse est mise en cache pour optimiser les performances.
        
        Returns:
            str: Code couleur hexadécimal (ex: #FF0000)
        """
        if self.useSpecificColor:
            return self.color
        else:
            cache_key = f"user:{self.user_id}"
            user = self.cache.get(cache_key)
            if user is None:
                user = self.user
                self.cache.set(cache_key, user, timeout=settings.LIMIT_CACHE_DEFAULT)
            d_c_p_service = DefaultColorPlaylistService(user)
            return d_c_p_service.get_default_color(self.typePlaylist)
        
    def get_color_text(self) -> str:
        """
        Récupère la couleur du texte de la playlist.
        
        Utilise la couleur de texte spécifique de la playlist si elle est définie,
        sinon utilise la couleur de texte par défaut de l'utilisateur pour ce type de playlist.
        La réponse est mise en cache pour optimiser les performances.
        
        Returns:
            str: Code couleur hexadécimal pour le texte (ex: #FFFFFF)
        """
        if self.useSpecificColor:
            return self.colorText
        else:
            cache_key = f"user:{self.user_id}"
            user = self.cache.get(cache_key)
            if user is None:
                user = self.user
                self.cache.set(cache_key, user, timeout=3600)
            d_c_p_service = DefaultColorPlaylistService(user)
            return d_c_p_service.get_default_color_text(self.typePlaylist)
            
    
    def clean(self) -> None:
        """
        Valide et nettoie les données du modèle.
        
        Détecte si l'icône a été modifiée pour les instances existantes.
        """
        if self.pk:
            self._icon_changed = self.icon != self._icon_original
        super().clean()
    
    def __replace_name_by_uuid(self) -> None:
        """
        Remplace le nom du fichier icône par un UUID.
        
        Génère un nouvel UUID et renomme le fichier icône en conservant l'extension.
        Cette méthode privée est utilisée lors de la sauvegarde pour éviter les conflits.
        """
        new_uuid = uuid.uuid4()
        self.icon.name = f"{new_uuid}.{self.icon.name.split('.')[-1]}"
    
    def __is_new_file(self) -> bool:
        """
        Détermine si un nouveau fichier icône a été uploadé.
        
        Returns:
            bool: True si l'icône a été modifiée, False sinon
        """
        return hasattr(self, '_icon_changed') and self._icon_changed
    
