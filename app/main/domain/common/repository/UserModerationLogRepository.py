from typing import Any, Optional, List
from main.architecture.persistence.models.UserModerationLog import UserModerationLog
from main.architecture.persistence.models.User import User
from django.db.models import QuerySet



class UserModerationLogRepository:

    def create(self, data: dict) -> UserModerationLog:
        moderation_log = UserModerationLog(**data)
        moderation_log.save()
        return moderation_log

    def get_resume_moderation(self, user: User, limit:int = 10) -> UserModerationLog|None:
        return  UserModerationLog.objects.filter(user=user).order_by('created_at')[:limit]

    def get_all_queryset(self) -> QuerySet[UserModerationLog]:
        return UserModerationLog.objects.all().order_by('created_at')
    
