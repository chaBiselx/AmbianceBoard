from django.db.models import Q
from ..models.FinalUser import FinalUser
from ..models.SoundBoard import SoundBoard

class SoundBoardFilter:
    def __init__(self, queryset=None):
        self.queryset = queryset or SoundBoard.objects.all()

    def filter_by_user_id(self, userId=None):
        final_users = FinalUser.objects.get(userID=userId)
        if userId:
            self.queryset = self.queryset.filter(finalUser_id=final_users)
        return self.queryset

 