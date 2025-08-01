from typing import Optional, List
from django.http import HttpRequest
from main.enum.PermissionEnum import PermissionEnum
from main.models.Playlist import Playlist
from main.filters.PlaylistFilter import PlaylistFilter
from main.forms.PlaylistForm import PlaylistForm
from main.factory.UserParametersFactory import UserParametersFactory
from main.utils.ServerNotificationBuilder import ServerNotificationBuilder


class PlaylistService:
    
    def __init__(self, request: HttpRequest) -> None:
        self.request = request
    
    def get_playlist(self, playlist_uuid: int) -> Optional[Playlist]:
        try:
            playlist = Playlist.objects.get(uuid=playlist_uuid)
            if not playlist or playlist.user != self.request.user:
                return None

            return playlist
        except Playlist.DoesNotExist:
            return None
        
    def get_all_playlist(self) -> List[Playlist]:
        try:
            _query_set = Playlist.objects.all().order_by('updated_at')
            _filter = PlaylistFilter(queryset=_query_set)
            playlists = _filter.filter_by_user(self.request.user)
        except Exception:
            playlists = []
        return playlists
    
    def save_form(self) -> Optional[Playlist]:
        user_parameters = UserParametersFactory(self.request.user)
        limit_playlist = user_parameters.limit_playlist
        
        if len(Playlist.objects.filter(user=self.request.user)) >= limit_playlist:
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
        