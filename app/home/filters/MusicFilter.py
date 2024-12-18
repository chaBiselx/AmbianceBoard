from django.db.models import Q
from django.contrib.auth.models import User
from ..models.Music import Music

class MusicFilter:
    def __init__(self, queryset=None):
        self.queryset = queryset or Music.objects.all()

    def filter_by_user(self, user=None):
        if user is not None:
            self.queryset = self.queryset.filter(playlist__user=user)
        return self.queryset

    def filter_by_playlist(self, id_playlist):
        if id_playlist:
            self.queryset = self.queryset.filter(playlist =id_playlist)
        return self.queryset

 