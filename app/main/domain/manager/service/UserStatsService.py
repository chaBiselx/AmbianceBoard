from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import datetime
from main.architecture.persistence.models.User import User

class UserStatsService:
    @staticmethod
    def get_user_activity_data(start_date: datetime, end_date: datetime) -> dict:
        """
        Récupère les données d'activité des utilisateurs entre deux dates.
        """
         # 1. Récupérer le nombre d'utilisateurs créés par jour
        users_created = User.objects.filter(
            date_joined__date__gte=start_date,
            date_joined__date__lte=end_date
        ).annotate(
            date=TruncDate('date_joined')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # 2. Récupérer le nombre de connexions par jour (based on last_login)
        users_connected = User.objects.filter(
            last_login__date__gte=start_date,
            last_login__date__lte=end_date,
            last_login__isnull=False  # Exclure les utilisateurs qui ne se sont jamais connectés
        ).annotate(
            date=TruncDate('last_login')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # 3. Formatter les données brutes (seulement les jours avec activité)
        created_data = []
        for item in users_created:
            created_data.append({
                'date': item['date'].strftime('%Y-%m-%d'),
                'count': item['count']
            })
        
        connected_data = []
        for item in users_connected:
            connected_data.append({
                'date': item['date'].strftime('%Y-%m-%d'),
                'count': item['count']
            })
        
        return {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'data': [
                {
                    'key' : 'users_created',
                    'label': 'Utilisateurs créés',
                    'data': created_data,
                },
                {
                    'key' : 'users_connected',
                    'label': 'Utilisateurs connectés',
                    'data': connected_data,
                }
            ]
        }