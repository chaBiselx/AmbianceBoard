import uuid
from typing import Any
from home.utils.uuidUtils import is_not_uuid_with_extension
from django.db import models
from home.models.User import User
from home.models.Playlist import Playlist
from home.models.SoundboardPlaylist import SoundboardPlaylist
from home.models.Tag import Tag
from home.message.ReduceSizeImgMessenger import reduce_size_img


# Create your models here.

class SoundBoard(models.Model):
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
    icon = models.FileField(upload_to=SOUNDBOARD_FOLDER, default=None, null=True, blank=True)
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._icon_original = self.icon if self.pk else None
        
    def __str__(self) -> str:
        return f"{self.name} ({self.uuid}) "    
        
    def save(self, *args: Any, **kwargs: Any) -> None:
        new_file = False
        if not hasattr(self, 'user') :
            raise ValueError("Playlist must have a user")
            
        if self.icon and ( is_not_uuid_with_extension(self.icon.name) or self.__is_new_file()): #Remplacement
            self.__replace_name_by_uuid()
            new_file = True
            
        super().save(*args, **kwargs)
        if new_file: 
            reduce_size_img.apply_async(args=[self.__class__.__name__, self.pk], queue='default', priority=1 )
            
    def update(self, *args: Any, **kwargs: Any) -> None:
        if not hasattr(self, 'user') :
            raise ValueError("Playlist must have a user")
            
        super().save(*args, **kwargs)
            

    def clean(self) -> None:
        if self.pk:
            self._icon_changed = self.icon != self._icon_original
        super().clean()
        
    def get_list_playlist_ordered(self) -> "QuerySet[Playlist]":
        return Playlist.objects.filter(soundboards=self).order_by('soundboardplaylist__order')
    
    def get_tags_list(self) -> "QuerySet[Tag]":
        """Retourne la liste des tags associés à ce soundboard"""
        return self.tags.filter(is_active=True).order_by('name')
    
    def add_tag(self, tag: Tag) -> None:
        """Ajoute un tag à ce soundboard"""
        if tag.is_active:
            self.tags.add(tag)
    
    def remove_tag(self, tag: Tag) -> None:
        """Retire un tag de ce soundboard"""
        self.tags.remove(tag)
        

        
 
    def __replace_name_by_uuid(self) -> None:
        new_uuid = uuid.uuid4()
        self.icon.name = f"{new_uuid}.{self.icon.name.split('.')[-1]}"
    
    def __is_new_file(self) -> bool :
        return hasattr(self, '_icon_changed') and self._icon_changed
    
