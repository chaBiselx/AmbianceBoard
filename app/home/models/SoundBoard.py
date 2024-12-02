from django.db import models
from .FinalUser import FinalUser
from .Playlist import Playlist

# Create your models here.

class SoundBoard(models.Model):
    finalUser =  models.ForeignKey(FinalUser, on_delete=models.CASCADE)
    playlists = models.ManyToManyField(Playlist)
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7)  # Format hexa (ex: #FFFFFF)
    colorText = models.CharField(max_length=7)  # Format hexa (ex: #FFFFFF)
    