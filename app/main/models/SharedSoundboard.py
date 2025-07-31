from typing import Any
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone
from datetime import datetime, timedelta

class SharedSoundboard(models.Model):
    """
    Modèle représentant un partage temporaire de soundboard.
    
    Permet de créer des liens de partage avec token pour donner
    accès temporaire à un soundboard à des utilisateurs non propriétaires.
    Les liens expirent automatiquement après 10 jours.
    """
    
    id = models.BigAutoField(primary_key=True) 
    soundboard = models.ForeignKey('SoundBoard', on_delete=models.CASCADE, null=False, blank=False, related_name='shared')
    token = models.UUIDField(default=uuid.uuid4, editable=False, null=False, blank=False)
    expiration_date = models.DateTimeField(default=timezone.now, null=False, blank=False)
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Sauvegarde le partage avec date d'expiration automatique.
        
        Définit automatiquement la date d'expiration à 10 jours après la création.
        
        Args:
            *args: Arguments positionnels pour la méthode save
            **kwargs: Arguments nommés pour la méthode save
        """
        self.expiration_date = timezone.make_aware(datetime.now() + timedelta(days=10))
        super().save(*args, **kwargs)
    
    
        
        
        