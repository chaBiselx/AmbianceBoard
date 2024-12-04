from django.db import models
from django.contrib.auth.models import User
from .Playlist import Playlist

# Create your models here.

class SoundBoard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    playlists = models.ManyToManyField(Playlist)
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7)  # Format hexa (ex: #FFFFFF)
    colorText = models.CharField(max_length=7)  # Format hexa (ex: #FFFFFF)
    
    def save(self, *args, **kwargs):
        if not self.user and self.request.user:
            self.user = self.request.user
        super().save(*args, **kwargs)
    