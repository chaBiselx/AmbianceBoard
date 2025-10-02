from typing import Any, Optional, List
from main.architecture.persistence.models.UserTier import UserTier
from main.architecture.persistence.models.User import User


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

    def get_user_query_set(self, related: str = 'user') -> Any:
        return UserTier.objects.select_related(related).all()
    
    def get_expired_user_tiers(self) -> List[UserTier]:
        return UserTier.objects.filter(expiration_date__lt=timezone.now())



