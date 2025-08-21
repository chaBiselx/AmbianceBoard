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
from main.models.UserActivity import UserActivity
from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum

User = get_user_model()


class UserActivityStatsService:
    """
    Service pour analyser les statistiques d'activité utilisateur.
    
    Fournit des méthodes pour générer divers rapports et analyses
    basés sur les données de traçage d'activité.
    """
    @staticmethod
    def get_user_nb_activity_data(start_date: datetime, end_date: datetime, activities: Optional[list[str]] = None) -> dict:

        if activities is None:
            activities =  UserActivityTypeEnum.values()

        # Récupération des données groupées par type d'activité et par date
        activity_data = UserActivity.objects.filter(
            start_date__gte=start_date,
            start_date__lte=end_date,
            activity_type__in=activities
        ).extra(
            select={'date': 'DATE(start_date)'}
        ).values('activity_type', 'date').annotate(
            count=Count('id')
        ).order_by('date', 'activity_type')
        
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
        
    # @staticmethod
    # def get_activity_counts_by_type(
    #     start_date: Optional[datetime] = None,
    #     end_date: Optional[datetime] = None
    # ) -> Dict[str, int]:
    #     """
    #     Obtient le nombre d'activités par type.
        
    #     Args:
    #         start_date: Date de début de la période
    #         end_date: Date de fin de la période
    #         user: Utilisateur spécifique (optionnel)
            
    #     Returns:
    #         Dict[str, int]: Dictionnaire avec les types d'activité et leurs comptes
    #     """
    #     queryset = UserActivity.objects.all()
        
    #     if start_date:
    #         queryset = queryset.filter(start_date__gte=start_date)
    #     if end_date:
    #         queryset = queryset.filter(start_date__lte=end_date)
        
    #     return dict(
    #         queryset.values('activity_type')
    #         .annotate(count=Count('id'))
    #         .values_list('activity_type', 'count')
    #     )
    
    # @staticmethod
    # def get_daily_activity_counts(
    #     days: int = 30,
    #     activity_type: Optional[UserActivityTypeEnum] = None
    # ) -> List[Dict[str, Any]]:
    #     """
    #     Obtient les comptes d'activité par jour sur une période.
        
    #     Args:
    #         days: Nombre de jours à analyser
    #         activity_type: Type d'activité spécifique (optionnel)
            
    #     Returns:
    #         List[Dict]: Liste des comptes par jour
    #     """
    #     end_date = timezone.now()
    #     start_date = end_date - timedelta(days=days)
        
    #     queryset = UserActivity.objects.filter(
    #         start_date__gte=start_date,
    #         start_date__lte=end_date
    #     )
        
    #     if activity_type:
    #         queryset = queryset.filter(activity_type=activity_type.name)
        
    #     return list(
    #         queryset.extra(
    #             select={'day': 'DATE(start_date)'}
    #         )
    #         .values('day')
    #         .annotate(count=Count('id'))
    #         .order_by('day')
    #     )
    
    # @staticmethod
    # def get_most_active_users(
    #     limit: int = 10,
    #     days: int = 30,
    #     activity_type: Optional[UserActivityTypeEnum] = None
    # ) -> List[Dict[str, Any]]:
    #     """
    #     Obtient les utilisateurs les plus actifs.
        
    #     Args:
    #         limit: Nombre d'utilisateurs à retourner
    #         days: Nombre de jours à analyser
    #         activity_type: Type d'activité spécifique (optionnel)
            
    #     Returns:
    #         List[Dict]: Liste des utilisateurs les plus actifs
    #     """
    #     end_date = timezone.now()
    #     start_date = end_date - timedelta(days=days)
        
    #     queryset = UserActivity.objects.filter(
    #         start_date__gte=start_date,
    #         start_date__lte=end_date,
    #         user__isnull=False
    #     )
        
    #     if activity_type:
    #         queryset = queryset.filter(activity_type=activity_type.name)
        
    #     return list(
    #         queryset.values('user__username', 'user__id')
    #         .annotate(activity_count=Count('id'))
    #         .order_by('-activity_count')[:limit]
    #     )
    
    # @staticmethod
    # def get_content_engagement_stats(
    #     content_type: str,
    #     days: int = 30
    # ) -> List[Dict[str, Any]]:
    #     """
    #     Obtient les statistiques d'engagement pour un type de contenu.
        
    #     Args:
    #         content_type: Type de contenu ('playlist', 'soundboard', etc.)
    #         days: Nombre de jours à analyser
            
    #     Returns:
    #         List[Dict]: Statistiques d'engagement par contenu
    #     """
    #     from django.contrib.contenttypes.models import ContentType
        
    #     end_date = timezone.now()
    #     start_date = end_date - timedelta(days=days)
        
    #     try:
    #         ct = ContentType.objects.get(model=content_type.lower())
    #     except ContentType.DoesNotExist:
    #         return []
        
    #     return list(
    #         UserActivity.objects.filter(
    #             start_date__gte=start_date,
    #             start_date__lte=end_date,
    #             content_type=ct,
    #             object_id__isnull=False
    #         )
    #         .values('object_id')
    #         .annotate(
    #             view_count=Count('id', filter=Q(activity_type__in=[
    #                 UserActivityTypeEnum.PLAYLIST_VIEW.name,
    #                 UserActivityTypeEnum.SOUNDBOARD_VIEW.name,
    #                 UserActivityTypeEnum.PAGE_VIEW.name
    #             ])),
    #             play_count=Count('id', filter=Q(activity_type__in=[
    #                 UserActivityTypeEnum.PLAYLIST_PLAY.name,
    #                 UserActivityTypeEnum.SOUNDBOARD_PLAY.name,
    #                 UserActivityTypeEnum.MUSIC_PLAY.name
    #             ])),
    #             total_interactions=Count('id')
    #         )
    #         .order_by('-total_interactions')
    #     )
    
    # @staticmethod
    # def get_error_analytics(days: int = 7) -> Dict[str, Any]:
    #     """
    #     Obtient des analyses des erreurs.
        
    #     Args:
    #         days: Nombre de jours à analyser
            
    #     Returns:
    #         Dict: Analyses des erreurs
    #     """
    #     end_date = timezone.now()
    #     start_date = end_date - timedelta(days=days)
        
    #     error_activities = UserActivity.objects.filter(
    #         start_date__gte=start_date,
    #         start_date__lte=end_date,
    #         activity_type__in=[
    #             UserActivityTypeEnum.ERROR_404.name,
    #             UserActivityTypeEnum.ERROR_500.name,
    #             UserActivityTypeEnum.ERROR_PERMISSION.name
    #         ]
    #     )
        
    #     error_counts = dict(
    #         error_activities.values('activity_type')
    #         .annotate(count=Count('id'))
    #         .values_list('activity_type', 'count')
    #     )
        
    #     return {
    #         'total_errors': error_activities.count(),
    #         'error_counts_by_type': error_counts,
    #         'period_start': start_date,
    #         'period_end': end_date
    #     }
