import uuid
from django.db import models
from django.core.validators import MinLengthValidator


class Tag(models.Model):
    """
    Modèle représentant un tag pour catégoriser les soundboards.
    
    Les tags permettent d'organiser et de filtrer les soundboards.
    Ils ont un nom unique, une description optionnelle et peuvent être 
    activés ou désactivés.
    """
    
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(
        max_length=50, 
        unique=True,
        validators=[MinLengthValidator(3)],
        help_text="Nom du tag (3-50 caractères)"
    )
    description = models.TextField(
        max_length=200, 
        blank=True,
        help_text="Description optionnelle du tag"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indique si le tag est actif et peut être utilisé"
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self) -> str:
        """
        Représentation textuelle du tag.
        
        Returns:
            str: Nom du tag
        """
        return f"{self.name}"

    def clean(self) -> None:
        """
        Valide et nettoie les données du modèle.
        
        Normalise le nom du tag en supprimant les espaces et en convertissant
        en minuscules pour assurer la cohérence.
        """
        if self.name:
            self.name = self.name.strip().lower()
