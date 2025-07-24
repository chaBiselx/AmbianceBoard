import uuid
from home.utils.uuidUtils import is_not_uuid_with_extension
from django.db import models
from home.models.User import User
from django.core.validators import MinValueValidator, MaxValueValidator
from home.enum.PlaylistTypeEnum import PlaylistTypeEnum
from home.strategy.PlaylistStrategy import PlaylistStrategy
from home.message.ReduceSizeImgMessenger import reduce_size_img
from home.models.SoundboardPlaylist import SoundboardPlaylist
from home.service.DefaultColorPlaylistService import DefaultColorPlaylistService
from django.core.cache import cache
from parameters import settings


class Playlist(models.Model):
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
    icon = models.FileField(upload_to=PLAYLIST_FOLDER, default=None, null=True, blank=True)
    useSpecificDelay = models.BooleanField(default=False, )
    maxDelay = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._icon_original = self.icon if self.pk else None
        
    def __str__(self):
        return f"{self.name} ({self.uuid}) "
        
    def save(self, *args, **kwargs):
        new_file = False
        if not hasattr(self, 'user') :
            raise ValueError("Playlist must have a user")
            
        if self.icon and  (is_not_uuid_with_extension(self.icon.name) or self.__is_new_file()): #Remplacement
            self.__replace_name_by_uuid()
            new_file = True

            
        super().save(*args, **kwargs)
        if new_file: 
            reduce_size_img.apply_async(args=[self.__class__.__name__, self.pk], queue='default', priority=1 )
            
    def update(self, *args, **kwargs):
        if not hasattr(self, 'user') :
            raise ValueError("Playlist must have a user")
            
        super().save(*args, **kwargs)
    
    def get_data_set(self):
        strategy = PlaylistStrategy().get_strategy(self.typePlaylist)
        return strategy.get_data(self)

    def get_order(self):
        soundboard_playlist = SoundboardPlaylist.objects.filter(Playlist=self).first()
        return soundboard_playlist.order if soundboard_playlist and soundboard_playlist.order is not None else None
    
    def get_color(self):
        if self.useSpecificColor:
            return self.color
        else:
            cache_key = f"user:{self.user_id}"
            user = cache.get(cache_key)
            if user is None:
                user = self.user 
                cache.set(cache_key, user, timeout=settings.LIMIT_CACHE_DEFAULT)
            d_c_p_service = DefaultColorPlaylistService(user)
            return d_c_p_service.get_default_color(self.typePlaylist)
        
    def get_color_text(self):
        if self.useSpecificColor:
            return self.colorText
        else:
            cache_key = f"user:{self.user_id}"
            user = cache.get(cache_key)
            if user is None:
                user = self.user 
                cache.set(cache_key, user, timeout=3600)
            d_c_p_service = DefaultColorPlaylistService(user)
            return d_c_p_service.get_default_color_text(self.typePlaylist)
            
    
    def clean(self):
        if self.pk:
            self._icon_changed = self.icon != self._icon_original
        super().clean()
    
    def __replace_name_by_uuid(self):
        new_uuid = uuid.uuid4()
        self.icon.name = f"{new_uuid}.{self.icon.name.split('.')[-1]}"
    
    def __is_new_file(self) -> bool :
        return hasattr(self, '_icon_changed') and self._icon_changed
    
