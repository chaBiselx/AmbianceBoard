from typing import Any, Optional, List
from main.architecture.persistence.models.UserActivity import UserActivity
from django.db.models import Count, Q, Avg, F, QuerySet, ExpressionWrapper, DurationField, Max
from django.db.models.functions import Floor, Extract
from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum
from main.architecture.persistence.models.User import User
from django.utils import timezone

class UserActivityRepository:
    
    def get(self, activity_uuid: str, activity_type: str) -> Optional[UserActivity]:
        try:
            return UserActivity.objects.get(uuid=activity_uuid, activity_type=activity_type)
        except UserActivity.DoesNotExist:
            return None

    def create(self, 
        activity_type: UserActivityTypeEnum,
        user: Optional[User] = None,
        content_object: Optional[Any] = None,
        session_key: Optional[str] = None,
    ) -> UserActivity:
        """
        Crée une nouvelle activité utilisateur.
        
        Args:
            activity_type: Type d'activité
            user: Utilisateur (None pour utilisateur anonyme)
            content_object: Objet associé à l'activité
            session_key: Clé de session
            
        Returns:
            UserActivity: Instance créée
        """
        activity = UserActivity(
            user=user,
            is_authenticated=user is not None and user.is_authenticated,
            activity_type=activity_type.value,
            content_object=content_object,
            session_key=session_key,
        )
        if session_key is None:
            activity.session_key = ''
        activity.save()
        return activity

    def get_activity_before(self, date):
        # Logic to retrieve user activities before the given date
        return UserActivity.objects.filter(start_date__lt=date)

    def get_activity_before_with_type(self, date, activity_type):
        # Logic to retrieve user activities before the given date and with specific activity types
        return UserActivity.objects.filter(start_date__lt=date, activity_type__in=activity_type)
    
    def get_activity_counts_by_date_and_type(self, start_date, end_date, activities):
        return UserActivity.objects.filter( 
            start_date__gte=start_date,
            start_date__lte=end_date,
            activity_type__in=activities
        ).extra(
            select={'date': 'DATE(start_date)'}
        ).values('activity_type', 'date').annotate(
            count=Count('id')
        ).order_by('date', 'activity_type')
        
    def get_frequentation(self, soundboard, start_date, end_date, activities):
        return UserActivity.objects.filter( 
            start_date__gte=start_date,
            start_date__lte=end_date,
            activity_type__in=activities,
            content_type__model='soundboard',
            object_id=soundboard.id
        ).extra(
            select={'date': 'DATE(start_date)'}
        ).values('activity_type', 'date').annotate(
            count=Count('id')
        ).order_by('date', 'activity_type')
        
    def get_average_session_duration(self, soundboard, start_date, end_date, activities, duration:str = 'min'):
        div = 1
        if  duration == 'min' :
            div = 60
        if  duration == 'h' :
            div = 3600
        
        return UserActivity.objects.filter( 
            start_date__gte=start_date,
            start_date__lte=end_date,
            activity_type__in=activities,
            content_type__model='soundboard',
            object_id=soundboard.id,
            end_date__isnull=False
        ).extra(
            select={'date': 'DATE(start_date)'}
        ).annotate(
            duration_seconds=Extract(F('end_date') - F('start_date'), 'epoch')
        ).values('activity_type', 'date').annotate(
            value=Floor(Avg('duration_seconds') / div)
        ).order_by('date', 'activity_type')
        
    def get_max_session_duration(self, soundboard, start_date, end_date, activities, duration:str = 'min'):
        div = 1
        if  duration == 'min' :
            div = 60
        if  duration == 'h' :
            div = 3600
        
        return UserActivity.objects.filter( 
            start_date__gte=start_date,
            start_date__lte=end_date,
            activity_type__in=activities,
            content_type__model='soundboard',
            object_id=soundboard.id,
            end_date__isnull=False
        ).extra(
            select={'date': 'DATE(start_date)'}
        ).annotate(
            duration_seconds=Extract(F('end_date') - F('start_date'), 'epoch')
        ).values('activity_type', 'date').annotate(
            value=Floor(Max('duration_seconds') / div)
        ).order_by('date', 'activity_type')
        
    
        

    
    