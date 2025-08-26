from django.db.models import Q
from main.models.User import User
from main.models.Track import Track

class MusicFilter:
    def __init__(self, queryset=None):
        self.queryset = queryset or Track.objects.all()

    def filter_by_user(self, user=None):
        if user is not None:
            self.queryset = self.queryset.filter(playlist__user=user)
        return self.queryset

    def filter_by_playlist(self, uuid_playlist):
        if uuid_playlist:
            self.queryset = self.queryset.filter(playlist__uuid=uuid_playlist)
        return self.queryset
    
   