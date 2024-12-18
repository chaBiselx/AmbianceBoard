import uuid
from django.db import models
from django.contrib.auth.models import User
from home.enum.PlaylistTypeEnum import PlaylistTypeEnum
from home.strategy.PlaylistStrategy import PlaylistStrategy


class Playlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=255)
    typePlaylist = models.CharField(max_length=64, choices=[
        (PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT, 'Son instantanné'),
        (PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT, 'Son d\'ambiance'),
        (PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC, 'Musique'),
    ])
    
    def save(self, *args, **kwargs):
        if not self.user and self.request.user:
            self.user = self.request.user
        super().save(*args, **kwargs)
        
    def getDataSet(self):
        strategy = PlaylistStrategy().get_strategy(self.typePlaylist)
        return strategy.get_data(self)
    

    
