import uuid
from typing import Any, Optional
from django.http import HttpRequest
from main.architecture.persistence.models.UserActivity import UserActivity
from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum
from django.utils import timezone

class ActivityContextHelper:
    """
    Gestionnaire de contexte pour tracer des activités avec durée.
    
    Permet de tracer des activités qui ne sont pas liées à des vues Django,
    comme des tâches en arrière-plan ou des opérations complexes.
    
    """
    
    @staticmethod
    def set_action(
        request: HttpRequest,
        activity_type: UserActivityTypeEnum,
        user: Optional[Any] = None,
        content_object: Optional[Any] = None
    ) -> UserActivity:
        """Démarre le traçage de l'activité."""
        activity = UserActivity.create_activity(
            activity_type=activity_type,
            user=user,
            session_key=request.session.session_key if request else None,
            content_object=content_object
        )
        return activity
    
    @staticmethod
    def find_activity(activity_uuid: uuid.UUID, activity_type: UserActivityTypeEnum) -> Optional[UserActivity]:
        """Recherche une activité par son UUID."""
        try:
            return UserActivity.objects.get(uuid=activity_uuid, activity_type=activity_type)
        except UserActivity.DoesNotExist:
            return None

    @staticmethod
    def set_end_action(activity: UserActivity):
        """Termine le traçage de l'activité."""
        if activity:
            activity.end_date = timezone.now()
            activity.save(update_fields=['end_date'])
        return activity
