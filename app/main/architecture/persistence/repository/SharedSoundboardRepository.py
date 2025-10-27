from typing import Any, Optional, List
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SharedSoundboard import SharedSoundboard
from django.utils import timezone


class SharedSoundboardRepository:
    
    def create(self, soundboard: SoundBoard) -> SharedSoundboard:
        return SharedSoundboard.objects.create(
            soundboard=soundboard
        )

    def get(self, soundboard: SoundBoard, token: str) -> SharedSoundboard|None:
        try:
            return SharedSoundboard.objects.filter(
                soundboard=soundboard,
                token=token
            ).first()
        except SharedSoundboard.DoesNotExist:
            return None

    def delete_expired(self):
        SharedSoundboard.objects.filter(expiration_date__lte=timezone.now()).delete()


