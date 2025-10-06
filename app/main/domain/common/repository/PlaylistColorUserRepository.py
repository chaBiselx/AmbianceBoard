from typing import Any, Optional, List
from main.architecture.persistence.models.PlaylistColorUser import PlaylistColorUser
from main.architecture.persistence.models.User import User
from main.domain.common.utils.logger import logger



class PlaylistColorUserRepository:

    def get_or_create(self, user: User, type_playlist: str) -> PlaylistColorUser:
        pcu, created = PlaylistColorUser.objects.get_or_create(user=user, typePlaylist=type_playlist)
        if created:
            pcu.user = user
            pcu.save()
        return pcu

    def get_list_with_user(self, user: User) -> List[PlaylistColorUser] | None:
        try:
            return PlaylistColorUser.objects.filter(user=user)
        except PlaylistColorUser.DoesNotExist:
            return None

    def get_list_with_user_and_type(self, user: User, playlist_type: str) -> List[PlaylistColorUser] | None:
        try:
            return PlaylistColorUser.objects.filter(user=user, typePlaylist=playlist_type)
        except PlaylistColorUser.DoesNotExist:
            return None

