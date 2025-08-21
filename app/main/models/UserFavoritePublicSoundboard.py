from django.db import models
from main.models.User import User
from main.models.SoundBoard import SoundBoard
from main.domain.common.enum.ThemeEnum import ThemeEnum
from django.core.validators import MinValueValidator, MaxValueValidator





class UserFavoritePublicSoundboard(models.Model):
   
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='favorite')
    uuidSoundboard = models.ForeignKey(SoundBoard, on_delete=models.CASCADE, null=False, blank=False, related_name='favorite')
    

    def get_soundboard(self):
        return self.uuidSoundboard
    
    
    
    
