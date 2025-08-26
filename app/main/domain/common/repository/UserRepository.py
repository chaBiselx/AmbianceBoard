from typing import Any, Optional, List
from main.models.User import User


class UserRepository:

    def get_user_by_email(self, email: str) -> Optional[User]:
        return User.objects.filter(email=email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return User.objects.filter(username=username).first()


