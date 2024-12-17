from django.db.models import Q
from django.contrib.auth.models import User
from ..models.Playlist import Playlist

class PlaylistFilter:
    def __init__(self, queryset=None):
        self.queryset = queryset or Playlist.objects.all()

    def filter_by_user(self, user=None):
        if user is not None:
            self.queryset = self.queryset.filter(user=user)
        return self.queryset

 