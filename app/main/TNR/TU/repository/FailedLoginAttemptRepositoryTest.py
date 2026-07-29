from django.test import TestCase, tag
from django.utils import timezone

from main.architecture.persistence.models.FailedLoginAttempt import FailedLoginAttempt
from main.architecture.persistence.repository.FailedLoginAttemptRepository import FailedLoginAttemptRepository


@tag('unitaire')
class FailedLoginAttemptRepositoryTest(TestCase):
    def setUp(self):
        self.repository = FailedLoginAttemptRepository()

    def test_get_or_create_creates_with_default_timestamp(self):
        item, created = self.repository.get_or_create('127.0.0.1', 'alice')

        self.assertTrue(created)
        self.assertEqual(item.ip_address, '127.0.0.1')
        self.assertEqual(item.username, 'alice')
        self.assertIsNotNone(item.timestamp)

    def test_get_or_create_respects_custom_defaults(self):
        ts = timezone.now() - timezone.timedelta(hours=1)

        item, created = self.repository.get_or_create(
            '10.1.1.1',
            'bob',
            defaults={'timestamp': ts, 'attempts': 3},
        )

        self.assertTrue(created)
        self.assertEqual(item.timestamp, ts)
        self.assertEqual(item.attempts, 3)

    def test_get_returns_first_match_or_none(self):
        FailedLoginAttempt.objects.create(ip_address='192.168.1.10', username='carol')

        found = self.repository.get('192.168.1.10', 'carol')
        missing = self.repository.get('192.168.1.10', 'missing')

        self.assertIsNotNone(found)
        self.assertEqual(found.username, 'carol')
        self.assertIsNone(missing)

    def test_delete_removes_matching_record(self):
        FailedLoginAttempt.objects.create(ip_address='8.8.8.8', username='dave')

        self.repository.delete('8.8.8.8', 'dave')

        self.assertFalse(FailedLoginAttempt.objects.filter(ip_address='8.8.8.8', username='dave').exists())
