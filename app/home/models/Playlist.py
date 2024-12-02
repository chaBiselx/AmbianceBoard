from django.db import models


# Create your models here.

class Playlist(models.Model):
    name = models.CharField(max_length=255)
