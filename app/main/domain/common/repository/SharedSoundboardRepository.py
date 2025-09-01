from typing import Any, Optional, List
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SharedSoundboard import SharedSoundboard


class SharedSoundboardRepository:

    def get(self, soundboard: SoundBoard, token: str) -> SharedSoundboard|None:
        try:
            return SharedSoundboard.objects.filter(
                soundboard=soundboard,
                token=token
            ).first()
        except SharedSoundboard.DoesNotExist:
            return None


