from typing import Optional, List
from django.http import HttpRequest
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.repository.PlaylistRepository import PlaylistRepository
from main.interface.ui.forms.private.PlaylistForm import PlaylistForm
from main.domain.common.factory.UserParametersFactory import UserParametersFactory
from main.domain.common.utils.ServerNotificationBuilder import ServerNotificationBuilder


class PlaylistService:
    
    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        self.playlist_repository = PlaylistRepository()

    def get_playlist(self, playlist_uuid: int) -> Optional[Playlist]:
        playlist = self.playlist_repository.get(playlist_uuid=playlist_uuid)
        if not playlist or playlist.user != self.request.user:
            return None

        return playlist
 
        
    def get_listing_playlist(self, filter:dict) -> List[Playlist]:
        return self.playlist_repository.get_listing_playlist(self.request.user, filter)


    def save_form(self) -> Optional[Playlist]:
        user_parameters = UserParametersFactory(self.request.user)
        limit_playlist = user_parameters.limit_playlist

        if self.playlist_repository.count_private(self.request.user) >= limit_playlist:
            ServerNotificationBuilder(self.request).set_message(
                "Vous avez atteint la limite de playlist total (" + str(limit_playlist) + ")."
            ).set_statut("error").send()
            return None

        form = PlaylistForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = self.request.user
            playlist.save()
            return playlist
        else:
            for(field, errors) in form.errors.items():
                for error in errors:
                    ServerNotificationBuilder(self.request).set_message(error).set_statut("error").send()
        return None
        