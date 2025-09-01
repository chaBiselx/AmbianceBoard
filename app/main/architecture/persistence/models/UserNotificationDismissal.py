from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from main.architecture.persistence.models.GeneralNotification import GeneralNotification
from main.architecture.persistence.models.User import User


class UserNotificationDismissal(models.Model):
    """
    Modèle pour tracker les notifications fermées par les utilisateurs.
    
    Permet de ne plus afficher une notification à un utilisateur spécifique
    une fois qu'il l'a fermée, même si elle est encore active.
    """
    
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        help_text="Utilisateur qui a fermé la notification"
    )
    
    notification = models.ForeignKey(
        GeneralNotification,
        on_delete=models.CASCADE,
        help_text="Notification qui a été fermée"
        
    )
    
    dismissed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure de fermeture de la notification"
    )
    
    class Meta:
        unique_together = ['user', 'notification']
        verbose_name = "Fermeture de notification"
        verbose_name_plural = "Fermetures de notifications"
        indexes = [
            models.Index(fields=['user', 'notification']),
            models.Index(fields=['dismissed_at']),
        ]
    
    def __str__(self) -> str:
        """
        Représentation textuelle de la fermeture de notification.
        
        Returns:
            str: Représentation de l'objet
        """
        return f"{self.user.username} a fermé la notification {self.notification.id} le {self.dismissed_at}"