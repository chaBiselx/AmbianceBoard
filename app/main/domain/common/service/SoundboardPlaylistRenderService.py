from django.http import HttpRequest
from django.template.loader import render_to_string

from main.architecture.persistence.repository.UserDevicePreferenceRepository import UserDevicePreferenceRepository
from main.architecture.persistence.repository.UserPreferenceRepository import UserPreferenceRepository
from main.domain.common.utils.DeviceDetector import detect_device_type


PLAYLIST_ITEM_TEMPLATE = 'Html/partial/soundboard/playlist_item.html'


class SoundboardPlaylistRenderService:
    """Centralise le rendu HTML d'une playlist dans un soundboard."""

    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        self.user_preference_repository = UserPreferenceRepository()
        self.user_device_preference_repository = UserDevicePreferenceRepository()

    def get_playlist_dim(self, default: int = 100) -> int:
        device_type = detect_device_type(self.request)
        user_preference = self.user_preference_repository.get_user_preferences(self.request.user)
        if not user_preference:
            return default

        device_preference = self.user_device_preference_repository.get_user_preferences(user_preference, device_type)
        if not device_preference:
            return default

        playlist_dim = device_preference.get_effective_playlist_dim()
        return playlist_dim if playlist_dim is not None else default

    def render_playlist_item(self, playlist, soundboard, master: bool = True, owner: bool = True) -> str:
        return render_to_string(PLAYLIST_ITEM_TEMPLATE, {
            'playlist': playlist,
            'soundboard': soundboard,
            'master': master,
            'owner': owner,
            'playlist_dim': self.get_playlist_dim(),
        })