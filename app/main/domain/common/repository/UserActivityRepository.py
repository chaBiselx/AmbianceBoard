from typing import Any, Optional, List
from main.architecture.persistence.models.UserActivity import UserActivity
from django.db.models import Count, Q, Avg, F, QuerySet

class UserActivityRepository:

    def get_activity_before(self, date):
        # Logic to retrieve user activities before the given date
        return UserActivity.objects.filter(start_date__lt=date)

    def get_activity_before_with_type(self, date, activity_type):
        # Logic to retrieve user activities before the given date and with specific activity types
        return UserActivity.objects.filter(start_date__lt=date, activity_type__in=activity_type)
    
    def get(self, start_date, end_date, activities):
        return UserActivity.objects.filter( 
            start_date__gte=start_date,
            start_date__lte=end_date,
            activity_type__in=activities
        ).extra(
            select={'date': 'DATE(start_date)'}
        ).values('activity_type', 'date').annotate(
            count=Count('id')
        ).order_by('date', 'activity_type')
    
    