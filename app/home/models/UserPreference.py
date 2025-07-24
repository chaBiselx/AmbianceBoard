from django.db import models
from home.models.User import User
from home.enum.ThemeEnum import ThemeEnum
from django.core.validators import MinValueValidator, MaxValueValidator





class UserPreference(models.Model):
   
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False, related_name='UserPreference')
    theme = models.CharField(max_length=50, choices=[
        (ThemeEnum.value, ThemeEnum.name) for ThemeEnum in ThemeEnum],
        verbose_name='Theme', default=ThemeEnum.LIGHT.value, blank=True)
    playlistDim =models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(500)], null=True, blank=True)
    soundboardDim =models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(500)], null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - Theme: {self.theme}"
    
    
    
    
