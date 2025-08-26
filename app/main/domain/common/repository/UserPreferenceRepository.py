from main.models.User import User
from main.models.UserPreference import UserPreference

class UserPreferenceRepository:

    def get_user_preferences(self, user: User) -> UserPreference:
        return UserPreference.objects.get(user=user)
        
