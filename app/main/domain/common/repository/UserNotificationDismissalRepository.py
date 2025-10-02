from typing import Any, Optional, List
from main.architecture.persistence.models.UserNotificationDismissal import UserNotificationDismissal
from main.architecture.persistence.models.User import User


class UserNotificationDismissalRepository:



    def dismiss_notification(self, user: User, notification_id:int ) -> UserNotificationDismissal|None:
        _,_ = UserNotificationDismissal.objects.get_or_create(
            user=user,
            notification_id=notification_id
        )
        return True



