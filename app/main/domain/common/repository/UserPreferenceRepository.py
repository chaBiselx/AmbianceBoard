from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.UserPreference import UserPreference

class UserPreferenceRepository:

    def get_user_preferences(self, user: User) -> UserPreference | None:
        try:
            return UserPreference.objects.get(user=user)
        except UserPreference.DoesNotExist:
            return None
