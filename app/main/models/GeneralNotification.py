import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class GeneralNotification(models.Model):
    """
    Modèle pour les notifications générales affichées à tous les utilisateurs.
    
    Permet d'afficher des messages temporaires avec du contenu HTML,
    ciblés vers les utilisateurs connectés ou non connectés.
    """
    uuid = models.UUIDField(
        db_index=True, 
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Identifiant unique de la notification"
    )
    message = models.TextField(
        help_text="Message de la notification en HTML"
    )
    class_name = models.CharField(
        max_length=64,
        help_text="Classe CSS pour le style de la notification",
        default='info',
        choices=[ # applys_boostrap_class
            ('info', 'Info'),
            ('warning', 'Warning'),
            ('error', 'Error'),
            ('success', 'Success'),
        ]
    )
    start_date = models.DateTimeField(
        help_text="Date et heure de début d'affichage de la notification",
        default=timezone.now
    )
    
    end_date = models.DateTimeField(
        help_text="Date et heure de fin d'affichage de la notification"
    )
    
    for_authenticated_users = models.BooleanField(
        default=True,
        help_text="Si True, la notification est réservée aux utilisateurs connectés. Si False, pour tous les utilisateurs."
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Permet de désactiver temporairement la notification sans la supprimer"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de création de la notification"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date de dernière modification"
    )
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Notification générale"
        verbose_name_plural = "Notifications générales"
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['is_active']),
        ]
    
    def clean(self):
        """Validation personnalisée du modèle."""
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError({
                'end_date': 'La date de fin doit être postérieure à la date de début.'
            })
    
    def save(self, *args, **kwargs):
        """Appelle la validation avant la sauvegarde."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def is_currently_active(self):
        """
        Vérifie si la notification est actuellement active.
        
        Returns:
            bool: True si la notification est active maintenant
        """
        if not self.is_active:
            return False
        
        now = timezone.now()
        return self.start_date <= now <= self.end_date


    def __str__(self):
        status = "Active" if self.is_currently_active() else "Inactive"
        target = "Connectés" if self.for_authenticated_users else "Tous"
        return f"Notification ({status}) - {target} - {self.start_date.strftime('%d/%m/%Y %H:%M')}"

