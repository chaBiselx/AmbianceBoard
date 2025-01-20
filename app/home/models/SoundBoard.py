import uuid
from home.utils.uuidUtils import is_not_uuid_with_extension
from django.db import models
from home.models.User import User
from home.models.Playlist import Playlist
from home.message.ReduceSizeImgMessenger import reduce_size_img


# Create your models here.

class SoundBoard(models.Model):
    SOUNDBOARD_FOLDER = 'soundBoardIcon/'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    playlists = models.ManyToManyField(Playlist, related_name='soundboards')
    name = models.CharField(max_length=255)
    color = models.CharField(default="#000000",max_length=7)  # Format hexa (ex: #FFFFFF)
    colorText = models.CharField(default="#ffffff",max_length=7)  # Format hexa (ex: #FFFFFF)
    is_public = models.BooleanField(default=False)
    icon = models.FileField(upload_to=SOUNDBOARD_FOLDER, default=None, null=True, blank=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._icon_original = self.icon if self.pk else None
    def save(self, *args, **kwargs):
        new_file = False
        if not hasattr(self, 'user') :
            raise ValueError("Playlist must have a user")
            
        if self.icon and ( is_not_uuid_with_extension(self.icon.name) or self.__is_new_file()): #Remplacement
            self.__replace_name_by_uuid()
            new_file = True
            
        super().save(*args, **kwargs)
        if new_file: 
            reduce_size_img.apply_async(args=[self.icon.path], queue='default', priority=1 )
            

    def clean(self):
        if self.pk:
            self._icon_changed = self.icon != self._icon_original
        super().clean()
 
    def __replace_name_by_uuid(self):
        new_uuid = uuid.uuid4()
        self.icon.name = f"{new_uuid}.{self.icon.name.split('.')[-1]}"
    
    def __is_new_file(self) -> bool :
        return hasattr(self, '_icon_changed') and self._icon_changed
    
