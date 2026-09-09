"""
Construction du contexte template nécessaire au panneau de scripts d'un soundboard.
"""

from typing import Any, Dict, TYPE_CHECKING

from django.conf import settings

from main.domain.common.service.script.SoundboardScriptSerializer import SoundboardScriptSerializer
from main.domain.common.service.script.SoundboardScriptService import SoundboardScriptService

if TYPE_CHECKING:
    from main.architecture.persistence.models.SoundBoard import SoundBoard


class ScriptContextHelper:

    @staticmethod
    def build(soundboard: "SoundBoard") -> Dict[str, Any]:
        """
        Construit le contexte du panneau de scripts.

        Args:
            soundboard: Soundboard affiché

        Returns:
            Dict[str, Any]: Contexte contenant les scripts actifs, leur JSON et le cooldown
        """
        scripts = SoundboardScriptService(soundboard).get_all_enabled()
        return {
            'scripts': scripts,
            'scripts_data': SoundboardScriptSerializer.serialize_many(scripts),
            'script_cooldown_ms': settings.SOUNDBOARD_SCRIPT_COOLDOWN_MS,
        }
