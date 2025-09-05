from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from main.domain.common.repository.UserRepository import UserRepository


class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_repository = UserRepository()
        user = user_repository.search_login_user(username)

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None