import uuid
from typing import Any, Dict

from django.db import models


class SoundboardScript(models.Model):
    """
    Script attaché à un soundboard.

    Un script regroupe une suite d'étapes déclenchables depuis le panneau
    « scripts » du soundboard. Il est rattaché au soundboard et jamais à une
    playlist en particulier.
    """

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    soundboard = models.ForeignKey(
        "SoundBoard",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='scripts',
    )
    name = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return f"{self.name} ({self.uuid})"

    def meta(self) -> Dict[str, Any]:
        return {
            "uuid": str(self.uuid),
            "name": self.name,
            "order": self.order,
            "enabled": self.enabled,
        }

    def get_ordered_steps(self):
        """
        Récupère les étapes du script triées par ordre d'affichage.

        Returns:
            QuerySet: Étapes ordonnées
        """
        return self.steps.all().order_by('order', 'id')
