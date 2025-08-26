from typing import Any, Optional, List
from main.models.UserModerationLog import UserModerationLog
from main.models.User import User


class UserModerationLogRepository:

 

    def get_resume_moderation(self, user: User, limit:int = 10) -> UserModerationLog|None:
        return  UserModerationLog.objects.filter(user=user).order_by('created_at')[:limit]



