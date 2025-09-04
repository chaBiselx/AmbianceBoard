from typing import Any, Optional, List
from main.architecture.persistence.models.PlaylistColorUser import PlaylistColorUser
from main.architecture.persistence.models.User import User


class PlaylistColorUserRepository:

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

