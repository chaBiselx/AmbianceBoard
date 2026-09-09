import uuid
from typing import Any, Dict

from django.core.exceptions import ValidationError
from django.db import models

from main.domain.common.enum.ScriptActionEnum import ScriptActionEnum
from main.domain.common.enum.ScriptTriggerEnum import ScriptTriggerEnum


class SoundboardScriptStep(models.Model):
    """
    Étape élémentaire d'un script de soundboard.

    Le couple (action_type, params) décrit l'opération à effectuer, le couple
    (trigger_type, trigger_offset_ms, trigger_source_step) décrit quand
    l'effectuer. Le JSONField `params` porte le payload propre à chaque action :
    c'est le point d'extension du schéma pour de nouvelles actions.
    """

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    script = models.ForeignKey(
        "SoundboardScript",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='steps',
    )
    order = models.IntegerField(default=0)
    action_type = models.CharField(
        max_length=50,
        choices=ScriptActionEnum.convert_to_choices(),
        default=ScriptActionEnum.PLAY_PLAYLIST.name,
    )
    trigger_type = models.CharField(
        max_length=50,
        choices=ScriptTriggerEnum.convert_to_choices(),
        default=ScriptTriggerEnum.IMMEDIATE.name,
    )
    trigger_offset_ms = models.PositiveIntegerField(default=0)
    trigger_source_step = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dependent_steps',
    )
    params = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return f"{self.script.name} - {self.order} - {self.action_type}"

    def clean(self) -> None:
        """
        Valide la cohérence du couple déclencheur / étape source.

        Raises:
            ValidationError: Si le déclencheur est incohérent
        """
        super().clean()
        if self.action_type not in ScriptActionEnum.names():
            raise ValidationError("Type d'action inconnu.")
        if self.trigger_type not in ScriptTriggerEnum.names():
            raise ValidationError("Type de déclencheur inconnu.")

        trigger = ScriptTriggerEnum[self.trigger_type]
        if trigger.require_source_step() and self.trigger_source_step is None:
            raise ValidationError("Le déclencheur ON_STEP_END nécessite une étape source.")
        if not trigger.require_source_step() and self.trigger_source_step is not None:
            raise ValidationError("Une étape source n'est autorisée que pour le déclencheur ON_STEP_END.")
        if self.trigger_source_step is not None and self.trigger_source_step.pk == self.pk:
            raise ValidationError("Une étape ne peut pas dépendre d'elle-même.")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)

    def meta(self) -> Dict[str, Any]:
        return {
            "uuid": str(self.uuid),
            "order": self.order,
            "action_type": self.action_type,
            "trigger_type": self.trigger_type,
            "trigger_offset_ms": self.trigger_offset_ms,
            "params": self.params,
        }
        
    def get_Playlist_uuid(self) -> str:
        return self.params.get("playlist_uuid", "")