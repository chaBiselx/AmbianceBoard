import uuid
from typing import Any
from main.utils.uuidUtils import is_not_uuid_with_extension
from django.db import models
from django.db.models import QuerySet
from main.models.User import User
from main.models.Playlist import Playlist
from main.models.SoundboardPlaylist import SoundboardPlaylist
from main.models.Tag import Tag
from main.message.ReduceSizeImgMessenger import reduce_size_img
from main.utils.OverwriteStorage import OverwriteStorage


# Create your models here.

class SoundBoard(models.Model):
    """
    Modèle représentant un soundboard contenant des playlists de musique.
    
    Un soundboard est un ensemble de playlists organisées par un utilisateur,
    avec des propriétés de personnalisation (couleurs, icône) et de visibilité.
    """
    
    SOUNDBOARD_FOLDER = 'soundBoardIcon/'
    id = models.BigAutoField(primary_key=True) 
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    playlists = models.ManyToManyField(Playlist, through=SoundboardPlaylist, related_name='soundboards')
    tags = models.ManyToManyField(Tag, blank=True, related_name='soundboards', help_text="Tags associés à ce soundboard")
    name = models.CharField(max_length=255)
    color = models.CharField(default="#000000",max_length=7)  # Format hexa (ex: #FFFFFF)
    colorText = models.CharField(default="#ffffff",max_length=7)  # Format hexa (ex: #FFFFFF)
    is_public = models.BooleanField(default=False)
    icon = models.FileField(upload_to=SOUNDBOARD_FOLDER, storage=OverwriteStorage(), default=None, null=True, blank=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialise une nouvelle instance de SoundBoard.
        
        Sauvegarde l'état original de l'icône pour détecter les changements.
        
        Args:
            *args: Arguments positionnels pour le modèle Django
            **kwargs: Arguments nommés pour le modèle Django
        """
        super().__init__(*args, **kwargs)
        self._icon_original = self.icon if self.pk else None
        
    def __str__(self) -> str:
        """
        Représentation textuelle du soundboard.
        
        Returns:
            str: Nom du soundboard suivi de son UUID entre parenthèses
        """
        return f"{self.name} ({self.uuid}) "    
        
    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Sauvegarde le soundboard avec traitement de l'icône.
        
        Vérifie la présence d'un utilisateur, renomme l'icône avec un UUID si nécessaire,
        et lance la tâche de réduction de taille d'image en arrière-plan.
        
        Args:
            *args: Arguments positionnels pour la méthode save
            **kwargs: Arguments nommés pour la méthode save
            
        Raises:
            ValueError: Si le soundboard n'a pas d'utilisateur associé
        """
        new_file = False
        if not hasattr(self, 'user') :
            raise ValueError("SoundBoard must have a user")
            
        if self.icon and ( is_not_uuid_with_extension(self.icon.name) or self.__is_new_file()): #Remplacement
            self.__replace_name_by_uuid()
            new_file = True
            
        super().save(*args, **kwargs)
        if new_file: 
            reduce_size_img.apply_async(args=[self.__class__.__name__, self.pk], queue='default', priority=1 )
            
    def update(self, *args: Any, **kwargs: Any) -> None:
        """
        Met à jour le soundboard.
        
        Vérifie la présence d'un utilisateur avant de sauvegarder.
        
        Args:
            *args: Arguments positionnels pour la méthode save
            **kwargs: Arguments nommés pour la méthode save
            
        Raises:
            ValueError: Si le soundboard n'a pas d'utilisateur associé
        """
        if not hasattr(self, 'user') :
            raise ValueError("SoundBoard must have a user")
            
        super().save(*args, **kwargs)
            

    def clean(self) -> None:
        """
        Valide et nettoie les données du modèle.
        
        Détecte si l'icône a été modifiée pour les instances existantes.
        """
        if self.pk:
            self._icon_changed = self.icon != self._icon_original
        super().clean()
        
    def get_list_playlist_ordered(self) -> "QuerySet[Playlist]":
        """
        Retourne la liste des playlists du soundboard ordonnées.
        
        Returns:
            QuerySet[Playlist]: QuerySet des playlists associées au soundboard,
                              ordonnées selon l'ordre défini dans SoundboardPlaylist
        """
        return Playlist.objects.filter(soundboards=self).order_by('soundboardplaylist__order')
    
    def get_tags_list(self) -> "QuerySet[Tag]":
        """
        Retourne la liste des tags associés à ce soundboard.
        
        Returns:
            QuerySet[Tag]: QuerySet des tags actifs associés au soundboard,
                          ordonnés par nom
        """
        return self.tags.filter(is_active=True).order_by('name')
    
    def add_tag(self, tag: Tag) -> None:
        """
        Ajoute un tag à ce soundboard.
        
        Le tag n'est ajouté que s'il est actif.
        
        Args:
            tag (Tag): Le tag à ajouter au soundboard
        """
        if tag.is_active:
            self.tags.add(tag)
    
    def remove_tag(self, tag: Tag) -> None:
        """
        Retire un tag de ce soundboard.
        
        Args:
            tag (Tag): Le tag à retirer du soundboard
        """
        self.tags.remove(tag)
        
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
    
