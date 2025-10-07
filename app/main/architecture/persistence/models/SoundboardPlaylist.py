from django.db import models
from django.core.exceptions import ValidationError



class SoundboardPlaylist(models.Model):
    SoundBoard = models.ForeignKey("SoundBoard", on_delete=models.CASCADE, null=False, blank=False)
    Playlist = models.ForeignKey("Playlist", on_delete=models.CASCADE, null=False, blank=False)
    order = models.IntegerField(default=0)
    section = models.IntegerField(default=1)
    activable_by_player = models.BooleanField(default=False)
    
    def clean(self):
        """Valide que la section est dans la plage autorisée"""
        super().clean()
        if self.section < 1 :
            raise ValidationError('La section doit être supérieure a 1.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    
    def __str__(self):
        return f"{self.SoundBoard} - {self.Playlist} - Section {self.section} - Ordre {self.order}"
    
    def meta(self):
        return {
            "SoundBoard": self.SoundBoard,
            "Playlist": self.Playlist,
            "order": self.order,
            "section": self.section,
        }
        
    
    def get_section(self) -> int:
        return self.section
    
    def get_playlist(self):
        return self.Playlist
