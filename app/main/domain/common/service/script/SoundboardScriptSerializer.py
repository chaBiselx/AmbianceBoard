"""
Sérialisation des scripts d'un soundboard vers le format consommé par le
moteur de script du frontend.
"""

import json
from typing import Any, Dict, List, TYPE_CHECKING

from main.architecture.persistence.models.SoundboardScript import SoundboardScript
from main.architecture.persistence.models.SoundboardScriptStep import SoundboardScriptStep

if TYPE_CHECKING:
    from main.architecture.persistence.models.SoundBoard import SoundBoard


class SoundboardScriptSerializer:
    """Convertit les scripts d'un soundboard en structures JSON."""

    @staticmethod
    def serialize_step(step: SoundboardScriptStep) -> Dict[str, Any]:
        return {
            "uuid": str(step.uuid),
            "order": step.order,
            "action_type": step.action_type,
            "trigger_type": step.trigger_type,
            "trigger_offset_ms": step.trigger_offset_ms,
            "trigger_source_step_uuid": (
                str(step.trigger_source_step.uuid) if step.trigger_source_step else None
            ),
            "params": step.params or {},
        }

    @classmethod
    def serialize_script(cls, script: SoundboardScript) -> Dict[str, Any]:
        return {
            "uuid": str(script.uuid),
            "name": script.name,
            "order": script.order,
            "enabled": script.enabled,
            "steps": [cls.serialize_step(step) for step in script.get_ordered_steps()],
        }

    @classmethod
    def serialize_many(cls, scripts: List[SoundboardScript]) -> List[Dict[str, Any]]:
        return [cls.serialize_script(script) for script in scripts]

    @classmethod
    def to_json(cls, scripts: List[SoundboardScript]) -> str:
        return json.dumps(cls.serialize_many(scripts))
