import uuid
from typing import Optional, Any
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from main.architecture.persistence.models.User import User
from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum


class UserActivity(models.Model):
    """
    Modèle de traçage des activités utilisateur.
    
    Ce modèle permet de tracer toutes les actions effectuées par les utilisateurs,
    qu'ils soient connectés ou non, avec la possibilité de mesurer la durée
    des actions et de les associer à des entités spécifiques (playlist, soundboard, etc.).
    """
    
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    
    # Informations utilisateur
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Utilisateur qui a effectué l'action (null si utilisateur non connecté)"
    )
    is_authenticated = models.BooleanField(
        default=False,
        help_text="Indique si l'utilisateur était connecté lors de l'action"
    )
    
    # Informations temporelles
    start_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date et heure de début de l'action",
        db_index=True
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date et heure de fin de l'action (pour mesurer la durée)"
    )
    
    # Type d'activité
    activity_type = models.CharField(
        max_length=64,
        choices=UserActivityTypeEnum.convert_to_choices(),
        help_text="Type d'activité effectuée par l'utilisateur",
        db_index=True
    )
    
    # Entité associée (générique pour pouvoir pointer vers n'importe quel modèle)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Type de l'entité associée (playlist, soundboard, etc.)"
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID de l'entité associée"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Données additionnelles
    session_key = models.CharField(
        max_length=40,
        blank=True,
        help_text="Clé de session pour identifier les utilisateurs non connectés",
        db_index=True
    )
    
    class Meta:
        """Métadonnées du modèle UserActivity."""
        
        verbose_name = "Activité utilisateur"
        verbose_name_plural = "Activités utilisateur"
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['start_date', 'activity_type']),
            models.Index(fields=['is_authenticated', 'activity_type']),
            models.Index(fields=['session_key', 'start_date']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self) -> str:
        """
        Représentation textuelle de l'activité.
        
        Returns:
            str: Description de l'activité avec utilisateur et type
        """
        if self.user:
            user_info = self.user.username
        elif self.session_key:
            user_info = f"Anonyme ({self.session_key[:8]}...)"
        else:
            user_info = "Anonyme"
        
        return f"{user_info} - {self.get_activity_type_display()} - {self.start_date}"
    
    def get_duration(self) -> Optional[float]:
        """
        Calcule la durée de l'activité en secondes.
        
        Returns:
            Optional[float]: Durée en secondes si end_date est défini, None sinon
        """
        if self.end_date:
            return (self.end_date - self.start_date).total_seconds()
        return None
    
    def set_end_time(self, end_time: Optional[Any] = None) -> None:
        """
        Définit la date de fin de l'activité.
        
        Args:
            end_time: Date de fin (utilise timezone.now() si None)
        """
        self.end_date = end_time or timezone.now()
        self.save(update_fields=['end_date'])
    
    def is_ongoing(self) -> bool:
        """
        Vérifie si l'activité est en cours.
        
        Returns:
            bool: True si l'activité n'a pas de date de fin, False sinon
        """
        return self.end_date is None
    

    
   
