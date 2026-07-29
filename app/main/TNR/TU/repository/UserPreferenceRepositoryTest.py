from django.test import TestCase, tag

from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.UserDevicePreference import UserDevicePreference
from main.architecture.persistence.models.UserPreference import UserPreference
from main.architecture.persistence.repository.UserDevicePreferenceRepository import UserDevicePreferenceRepository
from main.architecture.persistence.repository.UserPreferenceRepository import UserPreferenceRepository
from main.domain.common.enum.DeviceTypeEnum import DeviceTypeEnum


@tag('unitaire')
class UserPreferenceRepositoryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='prefs-user', password='pw')
        self.repository = UserPreferenceRepository()
        self.device_repository = UserDevicePreferenceRepository()

    def test_get_user_preferences_returns_none_when_missing(self):
        result = self.repository.get_user_preferences(self.user)

        self.assertIsNone(result)

    def test_get_user_preferences_returns_existing(self):
        created = UserPreference.objects.create(user=self.user)

        found = self.repository.get_user_preferences(self.user)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, created.id)

    def test_get_or_create_user_preferences_is_idempotent(self):
        first = self.repository.get_or_create_user_preferences(self.user)
        second = self.repository.get_or_create_user_preferences(self.user)

        self.assertEqual(first.id, second.id)
        self.assertEqual(UserPreference.objects.filter(user=self.user).count(), 1)

    def test_get_user_device_preferences_returns_none_or_existing(self):
        user_pref = self.repository.get_or_create_user_preferences(self.user)

        missing = self.device_repository.get_user_preferences(user_pref, DeviceTypeEnum.DESKTOP.value)
        self.assertIsNone(missing)

        created = UserDevicePreference.objects.create(
            user_preference=user_pref,
            device_type=DeviceTypeEnum.DESKTOP.value,
            playlist_dim=123,
            soundboard_dim=234,
        )
        found = self.device_repository.get_user_preferences(user_pref, DeviceTypeEnum.DESKTOP.value)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, created.id)

    def test_get_or_create_user_device_preferences_is_idempotent(self):
        user_pref = self.repository.get_or_create_user_preferences(self.user)

        first = self.device_repository.get_or_create_user_device_preferences(
            user_pref,
            DeviceTypeEnum.MOBILE.value,
        )
        second = self.device_repository.get_or_create_user_device_preferences(
            user_pref,
            DeviceTypeEnum.MOBILE.value,
        )

        self.assertEqual(first.id, second.id)
        self.assertEqual(
            UserDevicePreference.objects.filter(user_preference=user_pref, device_type=DeviceTypeEnum.MOBILE.value).count(),
            1,
        )
