from django.db.models import Q
from django.utils import timezone
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.GeneralNotification import GeneralNotification
from main.architecture.persistence.models.UserNotificationDismissal import UserNotificationDismissal


class GeneralNotificationFilter:
    def __init__(self, queryset=None):
        self.queryset = queryset or GeneralNotification.objects.all()
        
    def filter_by_active(self, is_active=True):
        self.queryset = self.queryset.filter(is_active=is_active)
        return self.queryset
    
    def filter_by_date(self):
        self.queryset = self.queryset.filter(
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )
        return self.queryset

    def filter_by_for_authenticated_users(self, is_authenticated=True):
        self.queryset = self.queryset.filter(for_authenticated_users=is_authenticated)
        return self.queryset

    def filter_by_user_has_notifications(self, user: User):
        self.queryset = self.queryset.exclude(id__in=UserNotificationDismissal.objects.filter(user=user).values_list('notification_id', flat=True))
        return self.queryset
