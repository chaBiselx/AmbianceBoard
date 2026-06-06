"""
Service de statistiques d'activité utilisateur.

Ce service fournit des méthodes pour analyser les données d'activité
et générer des statistiques d'usage de l'application.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from django.db.models import Count, Q, Avg, F, QuerySet
from django.utils import timezone
from django.contrib.auth import get_user_model
from main.architecture.persistence.models.UserActivity import UserActivity
from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum
from main.architecture.persistence.repository.UserActivityRepository import UserActivityRepository
from main.domain.common.service.BaseActivityStatsService import BaseActivityStatsService

User = get_user_model()


class UserActivityStatsService(BaseActivityStatsService):
    """
    Service pour analyser les statistiques d'activité utilisateur.
    
    Fournit des méthodes pour générer divers rapports et analyses
    basés sur les données de traçage d'activité.
    """
    def get_user_nb_activity_data(self, start_date: datetime, end_date: datetime) -> dict:
        activities =  list(UserActivityTypeEnum.listing_reporting_activities())
        activity_data = UserActivityRepository().get_activity_counts_by_date_and_type(start_date, end_date, activities)
        return self._generated_line_graph_data(start_date, end_date, activity_data)
        
    def get_error_activity_data(self, start_date: datetime, end_date: datetime) -> dict:
        activities =  list(UserActivityTypeEnum.listing_reporting_errors())
        activity_data = UserActivityRepository().get_activity_counts_by_date_and_type(start_date, end_date, activities)
        return self._generated_line_graph_data(start_date, end_date, activity_data)

    def get_top_active_users(self, start_date: datetime, end_date: datetime, limit: int = 10) -> list:
        activities = list(UserActivityTypeEnum.listing_reporting_activities())
        top_users = UserActivityRepository().get_top_active_users(start_date, end_date, activities, limit)

        return [
            {
                'rank': index,
                'user_uuid': user.get('user__uuid'),
                'username': user.get('user__username') or 'N/A',
                'email': user.get('user__email') or '',
                'activity_count': user.get('activity_count', 0)
            }
            for index, user in enumerate(top_users, start=1)
        ]

    def get_user_activities_queryset(self, user: User):
        return UserActivityRepository().get_user_activities_queryset(user)
