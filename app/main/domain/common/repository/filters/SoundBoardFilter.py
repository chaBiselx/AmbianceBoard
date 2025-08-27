from django.db.models import Q
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.SoundBoard import SoundBoard

class SoundBoardFilter:
    def __init__(self, queryset=None):
        self.queryset = queryset or SoundBoard.objects.all()

    def filter_by_user(self, user=None):
        if user is not None:
            self.queryset = self.queryset.filter(user=user)
        return self.queryset

 