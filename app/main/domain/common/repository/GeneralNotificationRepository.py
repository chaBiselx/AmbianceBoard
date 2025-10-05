from typing import List
from main.architecture.persistence.models.GeneralNotification import GeneralNotification
from main.architecture.persistence.models.User import User
from main.domain.common.repository.filters.GeneralNotificationFilter import GeneralNotificationFilter

class GeneralNotificationRepository:
    
    def get_list_notifications_actives(self, user: User|None) -> List[GeneralNotification]:
        general_notification_filter = GeneralNotificationFilter()
        general_notification_filter.filter_by_active(True)
        general_notification_filter.filter_by_date()
        if user is not None and user.is_authenticated:
            general_notification_filter.filter_by_user_has_notifications(user)
        else :
            general_notification_filter.filter_by_for_authenticated_users(False)
        return general_notification_filter.queryset.order_by('-start_date')

    def get_notification_by_uuid(self, uuid: str) -> GeneralNotification|None:
        try:
            return GeneralNotification.objects.get(uuid=uuid)
        except GeneralNotification.DoesNotExist:
            return None
