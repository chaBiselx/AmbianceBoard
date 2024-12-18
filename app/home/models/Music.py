import uuid
from django.db import models
from .Playlist import Playlist

class Music(models.Model):
    fileName = models.CharField(max_length=63)
    alternativeName = models.CharField(max_length=63, default=None)
    file = models.FileField(upload_to='musics/')
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.file:
            uuid = str(uuid.uuid4())
            
            self.file.name = f"{uuid}.{self.file.name.split('.')[-1]}"
        super().save(*args, **kwargs)
        
    
    def save(self, *args, **kwargs):
        if self.file:
            new_uuid = uuid.uuid4()
            self.fileName = self.file.name.split('.')[0][0:63]
            self.file.name = f"{new_uuid}.{self.file.name.split('.')[-1]}"
        super().save(*args, **kwargs)