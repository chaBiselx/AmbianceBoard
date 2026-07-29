from django.test import TestCase, tag
from django.utils import timezone

from main.architecture.persistence.models.GeneralNotification import GeneralNotification
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.UserNotificationDismissal import UserNotificationDismissal
from main.architecture.persistence.repository.GeneralNotificationRepository import GeneralNotificationRepository


@tag('unitaire')
class GeneralNotificationRepositoryTest(TestCase):
    def setUp(self):
        self.repository = GeneralNotificationRepository()
        self.user = User.objects.create_user(username='notif-user', password='pw')
        now = timezone.now()

        self.active_public = GeneralNotification.objects.create(
            message='active public',
            start_date=now - timezone.timedelta(hours=1),
            end_date=now + timezone.timedelta(hours=1),
            for_authenticated_users=False,
            is_active=True,
        )
        self.active_auth_only = GeneralNotification.objects.create(
            message='active auth only',
            start_date=now - timezone.timedelta(hours=2),
            end_date=now + timezone.timedelta(hours=2),
            for_authenticated_users=True,
            is_active=True,
        )
        self.inactive = GeneralNotification.objects.create(
            message='inactive',
            start_date=now - timezone.timedelta(hours=1),
            end_date=now + timezone.timedelta(hours=1),
            for_authenticated_users=False,
            is_active=False,
        )
        self.expired = GeneralNotification.objects.create(
            message='expired',
            start_date=now - timezone.timedelta(days=3),
            end_date=now - timezone.timedelta(days=1),
            for_authenticated_users=False,
            is_active=True,
        )

    def test_get_all_notifications_is_sorted_desc(self):
        values = list(self.repository.get_all_notifications())

        self.assertGreaterEqual(len(values), 4)
        self.assertGreaterEqual(values[0].start_date, values[-1].start_date)

    def test_get_list_notifications_actives_for_anonymous_filters_on_public_only(self):
        result = list(self.repository.get_list_notifications_actives(user=None))
        result_ids = {n.id for n in result}

        self.assertIn(self.active_public.id, result_ids)
        self.assertNotIn(self.active_auth_only.id, result_ids)
        self.assertNotIn(self.inactive.id, result_ids)
        self.assertNotIn(self.expired.id, result_ids)

    def test_get_list_notifications_actives_for_authenticated_excludes_dismissed(self):
        UserNotificationDismissal.objects.create(user=self.user, notification=self.active_auth_only)

        result = list(self.repository.get_list_notifications_actives(user=self.user))
        result_ids = {n.id for n in result}

        self.assertIn(self.active_public.id, result_ids)
        self.assertNotIn(self.active_auth_only.id, result_ids)

    def test_get_notification_by_uuid_returns_object_or_none(self):
        found = self.repository.get_notification_by_uuid(str(self.active_public.uuid))
        missing = self.repository.get_notification_by_uuid('00000000-0000-0000-0000-000000000000')

        self.assertIsNotNone(found)
        self.assertEqual(found.id, self.active_public.id)
        self.assertIsNone(missing)
