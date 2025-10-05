from typing import Any, Optional, List
from datetime import datetime

from django.db.models.functions import TruncDate
from django.db.models import Avg, Count
from django.db import models
from django.db.models import Q
from main.architecture.persistence.models.User import User


class UserRepository:
    

    
    def get_user(self, uuid_user: str) -> User | None:
        try:
            return User.objects.get(uuid=uuid_user)
        except User.DoesNotExist:
            return None


    def get_user_by_email(self, email: str) -> User | None:
        try:
            return User.objects.filter(email=email).first()
        except User.DoesNotExist:
            return None
    
    def get_user_by_username(self, username: str) -> User | None:
        try:
            return User.objects.filter(username=username).first()
        except User.DoesNotExist:
            return None
        
    def search_login_user(self, identifiant) -> User | None : 
        try:
            return User.objects.get(Q(username=identifiant) | Q(email=identifiant))
        except User.DoesNotExist:
            return None
        
    def get_stats_nb_user(self) -> int :
        return User.objects.all().count()
        
    def get_stats_avg_playlist_per_user(self) -> int : 
        return (User.objects.annotate(playlist_count=models.Count('playlist')).aggregate(avg_playlists=Avg('playlist_count')))['avg_playlists']
        
    def get_stats_avg_track_per_user(self) -> int : 
        return  User.objects.annotate(
        music_count=models.Count('playlist__tracks')
        ).aggregate(avg_music=Avg('music_count'))['avg_music']

    def get_list_user_in(self, user_ids: List[str]) -> List[User]:
        return User.objects.filter(uuid__in=user_ids)

    def get_stats_created(self, start_date: datetime, end_date: datetime) -> dict:
        return User.objects.filter(
            date_joined__date__gte=start_date,
            date_joined__date__lte=end_date
        ).annotate(
            date=TruncDate('date_joined')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

    def get_stats_connected(self, start_date: datetime, end_date: datetime) -> dict:
        return User.objects.filter(
            last_login__date__gte=start_date,
            last_login__date__lte=end_date,
            last_login__isnull=False  # Exclure les utilisateurs qui ne se sont jamais connectés
        ).annotate(
            date=TruncDate('last_login')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

    def get_inactive_users(self, cutoff_date) -> List[User]:
        return list(
            User.objects.filter(last_login__lte=cutoff_date)
        )
        
    def get_not_actived_users(self, cutoff_date) -> List[User]:
        return list(
            User.objects.filter(last_login=None, date_joined__lte=cutoff_date)
        )

    def get_not_confirmed_users(self, cutoff_date) -> List[User]:
        return list(
            User.objects.filter(isConfirmed=False, demandeConfirmationDate__lte=cutoff_date)
        )

