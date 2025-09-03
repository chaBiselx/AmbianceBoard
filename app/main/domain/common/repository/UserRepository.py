from typing import Any, Optional, List
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

