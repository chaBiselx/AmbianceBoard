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
