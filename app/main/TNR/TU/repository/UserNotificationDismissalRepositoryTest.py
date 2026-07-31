from django.test import TestCase, tag
from django.utils import timezone

from main.architecture.persistence.models.GeneralNotification import GeneralNotification
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.UserNotificationDismissal import UserNotificationDismissal
from main.architecture.persistence.repository.UserNotificationDismissalRepository import UserNotificationDismissalRepository


@tag('unitaire')
class UserNotificationDismissalRepositoryTest(TestCase):
    def setUp(self):
        self.repository = UserNotificationDismissalRepository()
        self.user = User.objects.create_user(username='dismiss-user', password='pw')

        now = timezone.now()
        self.notification_a = GeneralNotification.objects.create(
            message='A',
            start_date=now - timezone.timedelta(minutes=30),
            end_date=now + timezone.timedelta(minutes=30),
        )
        self.notification_b = GeneralNotification.objects.create(
            message='B',
            start_date=now - timezone.timedelta(minutes=30),
            end_date=now + timezone.timedelta(minutes=30),
        )

    def test_get_list_ids_returns_notification_ids(self):
        UserNotificationDismissal.objects.create(user=self.user, notification=self.notification_a)
        UserNotificationDismissal.objects.create(user=self.user, notification=self.notification_b)

        ids = self.repository.get_list_ids(self.user)

        self.assertEqual(set(ids), {self.notification_a.id, self.notification_b.id})

    def test_dismiss_notification_creates_once_and_returns_true(self):
        result_first = self.repository.dismiss_notification(self.user, self.notification_a.id)
        result_second = self.repository.dismiss_notification(self.user, self.notification_a.id)

        self.assertTrue(result_first)
        self.assertTrue(result_second)
        self.assertEqual(
            UserNotificationDismissal.objects.filter(user=self.user, notification=self.notification_a).count(),
            1,
        )
