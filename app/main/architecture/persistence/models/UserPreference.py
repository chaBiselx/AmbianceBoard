from django.db import models
from main.architecture.persistence.models.User import User
from main.domain.common.enum.ThemeEnum import ThemeEnum




class UserPreference(models.Model):
   
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False, related_name='UserPreference')
    theme = models.CharField(max_length=50, choices=[
        (ThemeEnum.value, ThemeEnum.name) for ThemeEnum in ThemeEnum],
        verbose_name='Theme', default=ThemeEnum.LIGHT.value, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - Theme: {self.theme}"
    
    
    
    
