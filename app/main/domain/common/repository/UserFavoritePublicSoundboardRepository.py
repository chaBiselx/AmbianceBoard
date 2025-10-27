
import uuid
from typing import Any, Optional, List
from django.contrib.auth.models import User
from main.architecture.persistence.models.UserFavoritePublicSoundboard import UserFavoritePublicSoundboard


class UserFavoritePublicSoundboardRepository:



    def get_or_create(self, user: User, uuid_soundboard:uuid ) -> UserFavoritePublicSoundboard|None:
        favorite , _ = UserFavoritePublicSoundboard.objects.get_or_create(user=user, uuidSoundboard=uuid_soundboard)
        return favorite
    
    def get_list_uuids(self, user: User) -> List[uuid.UUID]:
        if not user.is_authenticated:
            return []
        return list(
            UserFavoritePublicSoundboard.objects.filter(user=user)
            .values_list('uuidSoundboard__uuid', flat=True)
        )
