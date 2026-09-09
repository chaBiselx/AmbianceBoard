from typing import List, Optional

from main.architecture.persistence.models.SoundboardScript import SoundboardScript
from main.architecture.persistence.models.SoundboardScriptStep import SoundboardScriptStep


class SoundboardScriptStepRepository:

    def create(self, script: SoundboardScript, order: int, **kwargs) -> SoundboardScriptStep:
        return SoundboardScriptStep.objects.create(
            script=script,
            order=order,
            **kwargs
        )

    def get(self, script: SoundboardScript, step_uuid) -> Optional[SoundboardScriptStep]:
        try:
            return SoundboardScriptStep.objects.get(script=script, uuid=step_uuid)
        except (SoundboardScriptStep.DoesNotExist, ValueError):
            return None

    def get_all(self, script: SoundboardScript) -> List[SoundboardScriptStep]:
        return list(
            SoundboardScriptStep.objects
            .filter(script=script)
            .select_related('trigger_source_step')
            .order_by('order', 'id')
        )

    def get_last_index(self, script: SoundboardScript) -> Optional[int]:
        last_entry = SoundboardScriptStep.objects.filter(script=script).order_by('-order').first()
        return last_entry.order if last_entry else None

    def delete(self, step: SoundboardScriptStep) -> None:
        step.delete()

    def reorder(self, script: SoundboardScript, ordered_step_uuids: List[str]) -> None:
        steps = {str(step.uuid): step for step in self.get_all(script)}
        for index, step_uuid in enumerate(ordered_step_uuids):
            step = steps.get(str(step_uuid))
            if step:
                step.order = index
                step.save(update_fields=['order', 'updated_at'])
