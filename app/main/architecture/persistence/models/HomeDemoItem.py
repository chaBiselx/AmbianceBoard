import uuid
from django.db import models
from django.core.exceptions import ValidationError
from main.architecture.persistence.models.SoundBoard import SoundBoard


class HomeDemoItem(models.Model):
    """
    Element affiché dans la grille de démonstration de la page d'accueil.
    """

    uuid = models.UUIDField(
        db_index=True,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Identifiant unique de l'élément de démo"
    )
    title = models.CharField(
        max_length=120,
        verbose_name="Titre",
        help_text="Texte principal affiché sur la carte"
    )
    icon = models.CharField(
        max_length=8,
        verbose_name="Icône",
        help_text="Emoji ou petit texte d'icône (ex: ⚔️, 🌌)"
    )
    soundboard = models.ForeignKey(
        SoundBoard,
        on_delete=models.CASCADE,
        related_name='home_demo_items',
        limit_choices_to={'is_public': True},
        verbose_name="Soundboard public",
        help_text="Soundboard public ciblé par l'élément"
    )
    state_text = models.CharField(
        max_length=120,
        default="Cliquer pour jouer",
        verbose_name="Texte d'état",
        help_text="Texte secondaire affiché sous le titre"
    )
    aria_label = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Label accessibilité",
        help_text="Label aria personnalisé. Si vide, un label est généré automatiquement"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Permet d'activer ou désactiver l'élément sans le supprimer"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Élément de démo accueil"
        verbose_name_plural = "Éléments de démo accueil"
        indexes = [
            models.Index(fields=['is_active']),
        ]

    def get_aria_label(self) -> str:
        if self.aria_label:
            return self.aria_label
        return f"Jouer l'ambiance {self.title}"

    def clean(self):
        if self.soundboard_id and not self.soundboard.is_public:
            raise ValidationError({
                'soundboard': 'Le soundboard sélectionné doit être public.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} ({'actif' if self.is_active else 'inactif'})"
