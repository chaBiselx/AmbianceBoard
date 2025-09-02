"""
Décorateurs pour le traçage automatique des activités utilisateur.

Ces décorateurs permettent de tracer automatiquement les actions des utilisateurs
sans avoir à ajouter manuellement le code de traçage dans chaque vue.
"""

from typing import Any, Optional
from django.http import HttpRequest
from main.architecture.persistence.models.UserActivity import UserActivity
from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum

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
        user: Optional[Any] = None
    ) -> UserActivity:
        """Démarre le traçage de l'activité."""
        activity = UserActivity.create_activity(
            activity_type=activity_type,
            user=user,
            session_key=request.session.session_key if request else ''
        )
        return activity

    @staticmethod
    def set_end_action(activity: UserActivity):
        """Termine le traçage de l'activité."""
        if activity:
            activity.end_time = timezone.now()
            activity.save()
        return activity
