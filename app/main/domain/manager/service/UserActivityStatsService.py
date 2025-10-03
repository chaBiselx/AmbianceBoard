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
from main.domain.common.repository.UserActivityRepository import UserActivityRepository

User = get_user_model()


class UserActivityStatsService:
    """
    Service pour analyser les statistiques d'activité utilisateur.
    
    Fournit des méthodes pour générer divers rapports et analyses
    basés sur les données de traçage d'activité.
    """
    def get_user_nb_activity_data(self, start_date: datetime, end_date: datetime) -> dict:
        activities =  list(UserActivityTypeEnum.listing_reporting_activities())
        return self._generated_data(start_date, end_date, activities)
        
    def get_error_activity_data(self, start_date: datetime, end_date: datetime) -> dict:
        activities =  list(UserActivityTypeEnum.listing_reporting_errors())
        return self._generated_data(start_date, end_date, activities)

    def _generated_data(self, start_date: datetime, end_date: datetime, activities: List[str]) -> dict:
        # Récupération des données groupées par type d'activité et par date
        activity_data = UserActivityRepository().get(start_date, end_date, activities)
        
        # Organisation des données par type d'activité
        data_by_type = {}
        for item in activity_data:
            activity_type = item['activity_type']
            date = item['date'].strftime('%Y-%m-%d') if item['date'] else None
            count = item['count']
            
            if activity_type not in data_by_type:
                data_by_type[activity_type] = []
            
            data_by_type[activity_type].append({
                'date': date,
                'count': count
            })

        # Conversion en format de sortie structuré
        result_data = {}
        for activity_type, daily_counts in data_by_type.items():
            result_data[activity_type] = {
                'key': activity_type,
                'label': activity_type,
                'data': daily_counts
            }


        return {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'data': result_data
        }
        
    
        
  