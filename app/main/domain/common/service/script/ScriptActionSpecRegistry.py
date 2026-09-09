"""
Registre des spécifications de paramètres des actions de script.

Chaque action de script déclare ici les paramètres qu'elle attend et la façon
de les valider. Ajouter une action consiste à ajouter une spécification dans
`SPECS` (puis un handler équivalent côté frontend) : le reste du moteur
n'a pas à être modifié.
"""

from typing import Any, Dict, List, TYPE_CHECKING

from main.domain.common.enum.ScriptActionEnum import ScriptActionEnum
from main.domain.common.exceptions.SoundboardScriptException import InvalidScriptStepException

if TYPE_CHECKING:
    from main.architecture.persistence.models.SoundBoard import SoundBoard


class ScriptActionSpec:
    """Spécification des paramètres attendus par une action de script."""

    def __init__(self, required_keys: List[str], playlist_keys: List[str] | None = None):
        self.required_keys = required_keys
        self.playlist_keys = playlist_keys or []

    def validate(self, params: Dict[str, Any], soundboard: "SoundBoard") -> Dict[str, Any]:
        """
        Valide et normalise les paramètres d'une étape.

        Args:
            params: Paramètres bruts fournis par le client
            soundboard: Soundboard auquel appartient le script

        Returns:
            Dict[str, Any]: Paramètres normalisés, limités aux clés déclarées

        Raises:
            InvalidScriptStepException: Si un paramètre est absent ou invalide
        """
        if not isinstance(params, dict):
            raise InvalidScriptStepException("Les paramètres de l'étape doivent être un objet.")

        cleaned: Dict[str, Any] = {}
        for key in self.required_keys:
            if params.get(key) in (None, ''):
                raise InvalidScriptStepException(f"Le paramètre « {key} » est obligatoire.")
            cleaned[key] = params[key]

        for key in self.playlist_keys:
            cleaned[key] = str(cleaned[key])
            if not soundboard.playlists.filter(uuid=cleaned[key]).exists():
                raise InvalidScriptStepException("La playlist référencée n'appartient pas à ce soundboard.")

        return cleaned


class SetVolumeSpec(ScriptActionSpec):
    """Spécification de l'action SET_VOLUME, avec bornage du volume."""

    def validate(self, params: Dict[str, Any], soundboard: "SoundBoard") -> Dict[str, Any]:
        cleaned = super().validate(params, soundboard)
        try:
            volume = int(cleaned['volume'])
        except (TypeError, ValueError):
            raise InvalidScriptStepException("Le volume doit être un entier entre 0 et 100.")
        if volume < 0 or volume > 100:
            raise InvalidScriptStepException("Le volume doit être un entier entre 0 et 100.")
        cleaned['volume'] = volume
        return cleaned


class ScriptActionSpecRegistry:
    """Point d'extension : associe un type d'action à sa spécification."""

    SPECS: Dict[str, ScriptActionSpec] = {
        ScriptActionEnum.PLAY_PLAYLIST.name: ScriptActionSpec(
            required_keys=['playlist_uuid'], playlist_keys=['playlist_uuid']
        ),
        ScriptActionEnum.STOP_PLAYLIST.name: ScriptActionSpec(
            required_keys=['playlist_uuid'], playlist_keys=['playlist_uuid']
        ),
        ScriptActionEnum.SET_VOLUME.name: SetVolumeSpec(
            required_keys=['playlist_uuid', 'volume'], playlist_keys=['playlist_uuid']
        ),
        ScriptActionEnum.PLAY_TRACK.name: ScriptActionSpec(
            required_keys=['playlist_uuid', 'track_uuid'], playlist_keys=['playlist_uuid']
        ),
    }

    @classmethod
    def get(cls, action_type: str) -> ScriptActionSpec:
        """
        Récupère la spécification d'une action.

        Args:
            action_type: Nom technique de l'action

        Returns:
            ScriptActionSpec: Spécification associée

        Raises:
            InvalidScriptStepException: Si l'action est inconnue
        """
        spec = cls.SPECS.get(action_type)
        if spec is None:
            raise InvalidScriptStepException("Type d'action inconnu.")
        return spec

    @classmethod
    def validate(cls, action_type: str, params: Dict[str, Any], soundboard: "SoundBoard") -> Dict[str, Any]:
        return cls.get(action_type).validate(params, soundboard)

    @classmethod
    def required_keys(cls, action_type: str) -> List[str]:
        """
        Récupère les clés de paramètres attendues par une action.

        Args:
            action_type: Nom technique de l'action

        Returns:
            List[str]: Clés à collecter dans le formulaire
        """
        return list(cls.get(action_type).required_keys)
