from django.db import models
from main.architecture.persistence.models.UserPreference import UserPreference
from main.domain.common.enum.ThemeEnum import ThemeEnum
from main.domain.common.enum.DeviceTypeEnum import DeviceTypeEnum
from django.core.validators import MinValueValidator, MaxValueValidator


class UserDevicePreference(models.Model):
    """
    Modèle pour gérer les préférences spécifiques par type d'appareil.
    Permet à un utilisateur d'avoir des préférences différentes selon le support utilisé.
    """
    
    user_preference = models.ForeignKey(
        UserPreference, 
        on_delete=models.CASCADE, 
        null=False, 
        blank=False, 
        related_name='device_preferences'
    )
    device_type = models.CharField(
        max_length=50, 
        choices=[(DeviceTypeEnum.value, DeviceTypeEnum.name) for DeviceTypeEnum in DeviceTypeEnum],
        verbose_name='Type d\'appareil', 
        blank=False
    )

    playlist_dim = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(500)], 
        null=True, 
        blank=True,
        verbose_name='Dimension playlist spécifique',
        help_text='Si défini, remplace la dimension par défaut pour ce type d\'appareil'
    )
    soundboard_dim = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(500)], 
        null=True, 
        blank=True,
        verbose_name='Dimension soundboard spécifique',
        help_text='Si défini, remplace la dimension par défaut pour ce type d\'appareil'
    )
    
    class Meta:
        unique_together = ('user_preference', 'device_type')
        verbose_name = 'Préférence par appareil'
        verbose_name_plural = 'Préférences par appareil'
    
    def __str__(self):
        return f"{self.user_preference.user.username} - {self.device_type}"
    
    
    def get_effective_playlist_dim(self):
        """
        Retourne la dimension playlist effective pour cet appareil.
        """
        return self.playlist_dim
    
    def get_effective_soundboard_dim(self):
        """
        Retourne la dimension soundboard effective pour cet appareil.
        """
        return self.soundboard_dim
