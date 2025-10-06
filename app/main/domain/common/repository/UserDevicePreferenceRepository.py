from main.architecture.persistence.models.UserDevicePreference import UserDevicePreference
from main.architecture.persistence.models.UserPreference import UserPreference

class UserDevicePreferenceRepository:

    def get_user_preferences(self, user_preference: UserPreference, device_type: str) -> UserDevicePreference | None:
        try:
            return UserDevicePreference.objects.get(
                user_preference=user_preference,
                device_type=device_type
            )
            
        except UserDevicePreference.DoesNotExist:
            return None
        
    def get_or_create_user_device_preferences(self, user_preference: UserPreference, device_type: str) -> UserDevicePreference:
        user_device_pref, _ = UserDevicePreference.objects.get_or_create(
            user_preference=user_preference,
            device_type=device_type
        )
        return user_device_pref