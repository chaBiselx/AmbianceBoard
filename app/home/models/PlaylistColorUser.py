from django.db import models
from home.models.User import User
from home.enum.PlaylistTypeEnum import PlaylistTypeEnum


class PlaylistColorUser(models.Model):
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
        
    def __str__(self):
        return f"{self.user} ({self.typePlaylist}) "
        
   