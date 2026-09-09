"""
Énumération des déclencheurs d'une étape de script de soundboard.

Le déclencheur détermine à quel moment l'étape est exécutée par le moteur
de script côté client.
"""

from .BaseEnum import BaseEnum


class ScriptTriggerEnum(BaseEnum):
    """
    Énumération des types de déclencheurs d'une étape de script.

    - IMMEDIATE : exécutée dès le démarrage du script
    - TIMECODE : exécutée à `trigger_offset_ms` après le démarrage du script
    - ON_STEP_END : exécutée `trigger_offset_ms` après la fin de l'étape source
    """

    IMMEDIATE = 'Immediate'
    TIMECODE = 'Timecode'
    ON_STEP_END = 'OnStepEnd'

    @classmethod
    def names(cls) -> list:
        """
        Retourne la liste des noms techniques des déclencheurs.

        Returns:
            list: Noms des membres de l'énumération
        """
        return [member.name for member in cls]

    def require_source_step(self) -> bool:
        """
        Indique si le déclencheur nécessite une étape source.

        Returns:
            bool: True si une étape source est obligatoire
        """
        return self is ScriptTriggerEnum.ON_STEP_END
