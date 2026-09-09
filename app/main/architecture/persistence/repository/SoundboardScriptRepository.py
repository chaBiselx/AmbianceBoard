from typing import List, Optional, TYPE_CHECKING

from main.architecture.persistence.models.SoundboardScript import SoundboardScript

if TYPE_CHECKING:
    from main.architecture.persistence.models.SoundBoard import SoundBoard


class SoundboardScriptRepository:

    def create(self, soundboard: "SoundBoard", name: str, order: int, **kwargs) -> SoundboardScript:
        return SoundboardScript.objects.create(
            soundboard=soundboard,
            name=name,
            order=order,
            **kwargs
        )

    def get(self, soundboard: "SoundBoard", script_uuid) -> Optional[SoundboardScript]:
        try:
            return SoundboardScript.objects.get(soundboard=soundboard, uuid=script_uuid)
        except (SoundboardScript.DoesNotExist, ValueError):
            return None

    def get_all(self, soundboard: "SoundBoard") -> List[SoundboardScript]:
        return list(
            SoundboardScript.objects
            .filter(soundboard=soundboard)
            .prefetch_related('steps', 'steps__trigger_source_step')
            .order_by('order', 'id')
        )

    def get_all_enabled(self, soundboard: "SoundBoard") -> List[SoundboardScript]:
        return list(
            SoundboardScript.objects
            .filter(soundboard=soundboard, enabled=True)
            .prefetch_related('steps', 'steps__trigger_source_step')
            .order_by('order', 'id')
        )

    def get_last_index(self, soundboard: "SoundBoard") -> Optional[int]:
        last_entry = SoundboardScript.objects.filter(soundboard=soundboard).order_by('-order').first()
        return last_entry.order if last_entry else None

    def delete(self, script: SoundboardScript) -> None:
        script.delete()
