from django.db.models import Q
from home.models.User import User
from home.models.SoundBoard import SoundBoard

class SoundBoardFilter:
    def __init__(self, queryset=None):
        self.queryset = queryset or SoundBoard.objects.all()

    def filter_by_user(self, user=None):
        if user is not None:
            self.queryset = self.queryset.filter(user=user)
        return self.queryset

 