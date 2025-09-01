from django.db import models
from django.utils import timezone

class FailedLoginAttempt(models.Model):
    """
    Modèle pour traquer les tentatives de connexion échouées.
    
    Permet de détecter et prévenir les attaques par force brute
    en enregistrant les tentatives de connexion échouées par IP et nom d'utilisateur.
    """
    
    ip_address = models.GenericIPAddressField()
    username = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    attempts = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        """
        Représentation textuelle de la tentative de connexion échouée.
        
        Returns:
            str: Adresse IP, nom d'utilisateur et nombre de tentatives
        """
        return f"{self.ip_address} - {self.username}- {self.attempts} attempts"