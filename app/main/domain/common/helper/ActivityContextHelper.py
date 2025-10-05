import uuid
from typing import Any, Optional
from django.http import HttpRequest
from main.architecture.persistence.models.UserActivity import UserActivity
from main.domain.common.repository.UserActivityRepository import UserActivityRepository
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
        # Vérifier si l'utilisateur est authentifié et valide
        authenticated_user = None
        if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
            authenticated_user = user
        
        activity = UserActivity.create_activity( #TODO repository
            activity_type=activity_type,
            user=authenticated_user,
            session_key=request.session.session_key if request else '',
            content_object=content_object
        )
        return activity
    
    @staticmethod
    def find_activity(activity_uuid: uuid.UUID, activity_type: UserActivityTypeEnum) -> Optional[UserActivity]:
        """Recherche une activité par son UUID."""
        return UserActivityRepository().get(activity_uuid=activity_uuid, activity_type=activity_type)
       

    @staticmethod
    def set_end_action(activity: UserActivity):
        """Termine le traçage de l'activité."""
        if activity:
            activity.end_date = timezone.now()
            activity.save(update_fields=['end_date'])
        return activity
