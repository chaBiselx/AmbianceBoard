from django.db.models import Q
from home.models.User import User
from home.models.Playlist import Playlist

class PlaylistFilter:
    def __init__(self, queryset=None):
        self.queryset = queryset or Playlist.objects.all()

    def filter_by_user(self, user=None):
        if user is not None:
            self.queryset = self.queryset.filter(user=user)
        return self.queryset

    def filter_by_playlist(self, id_playlist):
        if id_playlist:
            self.queryset = self.queryset.filter(playlist_uuid=id_playlist)
        return self.queryset

 