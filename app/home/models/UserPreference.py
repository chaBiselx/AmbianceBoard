from django.db import models
from home.models.User import User
from home.enum.ThemeEnum import ThemeEnum
from django.core.validators import MinValueValidator, MaxValueValidator





class UserPreference(models.Model):
   
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False, related_name='UserPreference')
    theme = models.CharField(max_length=50, choices=[
        (ThemeEnum.name, ThemeEnum.value) for ThemeEnum in ThemeEnum],
        verbose_name='Theme', default=None, blank=True,null=True)
    playlistDim =models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(500)], null=True, blank=True)
    SoundboardDim =models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(500)], null=True, blank=True)
    
    
    
    
