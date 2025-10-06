from typing import Any, Optional, List
from main.architecture.persistence.models.UserTier import UserTier
from main.architecture.persistence.models.User import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import QuerySet




class UserTiersRepository:
    
    

    def get(self, user: User) -> UserTier:
        try:
            return UserTier.objects.get(user=user)
        except UserTier.DoesNotExist:
            return self.create(user)

    def create(self, user: User, tier_name='STANDARD') -> UserTier:
        return UserTier.objects.create(
            user=user,
            tier_name=tier_name
        )
        
    def get_or_create(self, user: User) -> UserTier:
        user_tier, _ = UserTier.objects.get_or_create(user=user)
        return user_tier

    def get_user_query_set(self, related: str = 'user') -> Any:
        return UserTier.objects.select_related(related).all()
    
    def get_expired_user_tiers(self) -> List[UserTier]:
        return UserTier.objects.filter(expiration_date__lt=timezone.now())
    
    def get_expired_user_premium_tiers(self):
        now = timezone.now()
        return UserTier.objects.filter(
                tier_expiry_date__lt=now,
                tier_name__in=['PREMIUM_BASIC', 'PREMIUM_ADVANCED', 'PREMIUM_PRO']
            )

    def get_upcoming_expirations_user_tiers(self, delta_days: int) -> List[UserTier]:
        now = timezone.now()
        warning_threshold = now + timedelta(days=delta_days)
        return UserTier.objects.filter(
            tier_expiry_date__lte=warning_threshold,
            tier_expiry_date__gt=now,
            tier_name__in=['PREMIUM_BASIC', 'PREMIUM_ADVANCED', 'PREMIUM_PRO']
        )
        
    def get_count_user_tiers(self, tier_name:str) -> int:
        return UserTier.objects.filter(tier_name=tier_name).count()
    
    def get_count_expiring_soon(self, days:int) -> int:
        expiry_threshold = timezone.now() + timedelta(days=days)
        return UserTier.objects.filter(
            tier_expiry_date__lte=expiry_threshold,
            tier_expiry_date__gte=timezone.now(),
        ).count()

    def get_upcoming_expirations_queryset(self, days:int) -> QuerySet[UserTier]:
        expiry_threshold = timezone.now() + timedelta(days=days)
        return UserTier.objects.filter(
            tier_expiry_date__lte=expiry_threshold,
        ).select_related('user').order_by('tier_expiry_date')

    def get_count_expired(self) -> int:
        return UserTier.objects.filter(  
            tier_expiry_date__lt=timezone.now(),
        ).count()
        
    



