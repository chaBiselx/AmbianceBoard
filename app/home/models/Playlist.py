import uuid
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Playlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=255)
    typePlaylist = models.CharField(max_length=64, choices=[
        ('Instant', 'Son instantanné'),
        ('Ambient', 'Son d\'ambiance'),
        ('Musique', 'Musique'),
    ])
    
    def save(self, *args, **kwargs):
        if not self.user and self.request.user:
            self.user = self.request.user
        super().save(*args, **kwargs)
    
