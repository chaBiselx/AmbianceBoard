import uuid
from django.db import models
from home.models.User import User
from home.models.Playlist import Playlist

# Create your models here.

class SoundBoard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    playlists = models.ManyToManyField(Playlist, related_name='soundboards')
    name = models.CharField(max_length=255)
    color = models.CharField(default="#000000",max_length=7)  # Format hexa (ex: #FFFFFF)
    colorText = models.CharField(default="#ffffff",max_length=7)  # Format hexa (ex: #FFFFFF)
    is_public = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.user and self.request.user:
            self.user = self.request.user
        super().save(*args, **kwargs)
    