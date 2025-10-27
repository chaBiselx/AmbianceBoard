from datetime import datetime
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.UserRepository import UserRepository



class UserStatsService:
    @staticmethod
    def get_user_activity_data(start_date: datetime, end_date: datetime) -> dict:
        """
        Récupère les données d'activité des utilisateurs entre deux dates.
        """
        user_repository = UserRepository()
         # 1. Récupérer le nombre d'utilisateurs créés par jour
        users_created = user_repository.get_stats_created(start_date, end_date)  # Utilisation du repository

        # 2. Récupérer le nombre de connexions par jour (based on last_login)
        users_connected = user_repository.get_stats_connected(start_date, end_date)  # Utilisation du repository
        
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