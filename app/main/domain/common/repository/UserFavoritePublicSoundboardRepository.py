
import uuid
from django.contrib.auth.models import User
from typing import Any, Optional, List
from main.architecture.persistence.models.UserFavoritePublicSoundboard import UserFavoritePublicSoundboard


class UserFavoritePublicSoundboardRepository:



    def get_or_create(self, user: User, uuid_soundboard:uuid ) -> UserFavoritePublicSoundboard|None:
        favorite , _ = UserFavoritePublicSoundboard.objects.get_or_create(user=user, uuidSoundboard=uuid_soundboard)
        return favorite
