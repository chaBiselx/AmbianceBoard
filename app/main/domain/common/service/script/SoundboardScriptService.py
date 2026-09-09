"""
Service métier de gestion des scripts de soundboard.

Assure le CRUD des scripts et de leurs étapes, en validant les paramètres via
le ScriptActionSpecRegistry et la cohérence des déclencheurs.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from django.core.exceptions import ValidationError

from main.architecture.persistence.models.SoundboardScript import SoundboardScript
from main.architecture.persistence.models.SoundboardScriptStep import SoundboardScriptStep
from main.architecture.persistence.repository.SoundboardScriptRepository import SoundboardScriptRepository
from main.architecture.persistence.repository.SoundboardScriptStepRepository import SoundboardScriptStepRepository
from main.domain.common.enum.ScriptTriggerEnum import ScriptTriggerEnum
from main.domain.common.exceptions.SoundboardScriptException import InvalidScriptStepException
from main.domain.common.service.script.ScriptActionSpecRegistry import ScriptActionSpecRegistry

if TYPE_CHECKING:
    from main.architecture.persistence.models.SoundBoard import SoundBoard


class SoundboardScriptService:
    """Service de gestion des scripts rattachés à un soundboard."""

    def __init__(self, soundboard: "SoundBoard"):
        self.soundboard = soundboard
        self.script_repository = SoundboardScriptRepository()
        self.step_repository = SoundboardScriptStepRepository()


    def get_all(self) -> List[SoundboardScript]:
        return self.script_repository.get_all(self.soundboard)

    def get_all_enabled(self) -> List[SoundboardScript]:
        return self.script_repository.get_all_enabled(self.soundboard)

    def get(self, script_uuid) -> Optional[SoundboardScript]:
        return self.script_repository.get(self.soundboard, script_uuid)

    def create(self, name: str, **kwargs) -> SoundboardScript:
        last_index = self.script_repository.get_last_index(self.soundboard)
        order = 0 if last_index is None else last_index + 1
        return self.script_repository.create(self.soundboard, name=name, order=order, **kwargs)

    def update(self, script: SoundboardScript, **fields) -> SoundboardScript:
        allowed = {'name', 'enabled', 'order'}
        for key, value in fields.items():
            if key in allowed:
                setattr(script, key, value)
        script.save()
        return script

    def delete(self, script: SoundboardScript) -> None:
        self.script_repository.delete(script)

    def add_step(
        self,
        script: SoundboardScript,
        action_type: str,
        trigger_type: str,
        params: Dict[str, Any],
        trigger_offset_ms: int = 0,
        trigger_source_step_uuid: Optional[str] = None,
    ) -> SoundboardScriptStep:
        """
        Ajoute une étape à la fin d'un script.

        Raises:
            InvalidScriptStepException: Si l'action, le déclencheur ou les
                paramètres sont invalides
        """
        cleaned_params = ScriptActionSpecRegistry.validate(action_type, params, self.soundboard)
        source_step = self.__resolve_source_step(script, trigger_type, trigger_source_step_uuid)
        last_index = self.step_repository.get_last_index(script)
        order = 0 if last_index is None else last_index + 1

        try:
            return self.step_repository.create(
                script,
                order=order,
                action_type=action_type,
                trigger_type=trigger_type,
                trigger_offset_ms=max(0, int(trigger_offset_ms or 0)),
                trigger_source_step=source_step,
                params=cleaned_params,
            )
        except (ValidationError, ValueError) as error:
            raise InvalidScriptStepException(str(error)) from error

    def update_step(
        self,
        script: SoundboardScript,
        step: SoundboardScriptStep,
        action_type: str,
        trigger_type: str,
        params: Dict[str, Any],
        trigger_offset_ms: int = 0,
        trigger_source_step_uuid: Optional[str] = None,
    ) -> SoundboardScriptStep:
        cleaned_params = ScriptActionSpecRegistry.validate(action_type, params, self.soundboard)
        source_step = self.__resolve_source_step(script, trigger_type, trigger_source_step_uuid, current_step=step)

        step.action_type = action_type
        step.trigger_type = trigger_type
        step.trigger_offset_ms = max(0, int(trigger_offset_ms or 0))
        step.trigger_source_step = source_step
        step.params = cleaned_params
        try:
            step.save()
        except (ValidationError, ValueError) as error:
            raise InvalidScriptStepException(str(error)) from error
        return step

    def delete_step(self, step: SoundboardScriptStep) -> None:
        self.step_repository.delete(step)

    def reorder_steps(self, script: SoundboardScript, ordered_step_uuids: List[str]) -> None:
        self.step_repository.reorder(script, ordered_step_uuids)

    def __resolve_source_step(
        self,
        script: SoundboardScript,
        trigger_type: str,
        trigger_source_step_uuid: Optional[str],
        current_step: Optional[SoundboardScriptStep] = None,
    ) -> Optional[SoundboardScriptStep]:
        if trigger_type not in ScriptTriggerEnum.names():
            raise InvalidScriptStepException("Type de déclencheur inconnu.")

        if not ScriptTriggerEnum[trigger_type].require_source_step():
            return None

        if not trigger_source_step_uuid:
            raise InvalidScriptStepException("Le déclencheur ON_STEP_END nécessite une étape source.")

        source_step = self.step_repository.get(script, trigger_source_step_uuid)
        if source_step is None:
            raise InvalidScriptStepException("L'étape source est introuvable dans ce script.")
        if current_step is not None and source_step.pk == current_step.pk:
            raise InvalidScriptStepException("Une étape ne peut pas dépendre d'elle-même.")
        if current_step is not None and self.__creates_cycle(source_step, current_step):
            raise InvalidScriptStepException("Les dépendances entre étapes forment un cycle.")
        return source_step

    def __creates_cycle(self, source_step: SoundboardScriptStep, current_step: SoundboardScriptStep) -> bool:
        visited = set()
        cursor = source_step
        while cursor is not None:
            if cursor.pk == current_step.pk:
                return True
            if cursor.pk in visited:
                return False
            visited.add(cursor.pk)
            cursor = cursor.trigger_source_step
        return False
