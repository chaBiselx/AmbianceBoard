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


class UserPublicActivityStatsService(BaseActivityStatsService):
    """
    Service pour analyser les statistiques d'activité utilisateur.
    
    Fournit des méthodes pour générer divers rapports et analyses
    basés sur les données de traçage d'activité.
    """
    def get_frequentation(self, soundboard, start_date: datetime, end_date: datetime) -> dict:
        activities =  [UserActivityTypeEnum.SOUNDBOARD_VIEW]
        activity_data = UserActivityRepository().get_frequentation(soundboard, start_date, end_date, activities)
        return self._generated_line_graph_data(start_date, end_date, activity_data, transposition_titles={UserActivityTypeEnum.SOUNDBOARD_VIEW.value: "Vues"})
    
    def get_moyenne_duration_session(self, soundboard, start_date: datetime, end_date: datetime) -> dict:
        activities =  [UserActivityTypeEnum.SOUNDBOARD_VIEW]
        activity_data1 = list(UserActivityRepository().get_average_session_duration(soundboard, start_date, end_date, activities))
        activity_data2 = list(UserActivityRepository().get_max_session_duration(soundboard, start_date, end_date, activities))
        for item in activity_data2:
            item['activity_type'] = 'max_' + item['activity_type']
        data = activity_data1 + activity_data2
        return self._generated_bar_graph_data(start_date, end_date, data, transposition_titles={UserActivityTypeEnum.SOUNDBOARD_VIEW.value: "Durée Moyenne des Sessions (min)", 'max_' + UserActivityTypeEnum.SOUNDBOARD_VIEW.value: "Durée Max des Sessions (min)"})