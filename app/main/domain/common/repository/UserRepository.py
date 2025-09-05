from typing import Any, Optional, List

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
   

