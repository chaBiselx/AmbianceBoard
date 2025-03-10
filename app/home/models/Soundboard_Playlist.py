from django.db import models



class Soundboard_Playlist(models.Model):
    SoundBoard = models.ForeignKey("SoundBoard", on_delete=models.CASCADE, null=False, blank=False)
    Playlist = models.ForeignKey("Playlist", on_delete=models.CASCADE, null=False, blank=False)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.SoundBoard} - {self.Playlist} - {self.order}"
    
    def meta(self):
        return {
            "SoundBoard": self.SoundBoard,
            "Playlist": self.Playlist,
            "order": self.order,
        }
