
from django.test import TestCase, RequestFactory
from django.utils import timezone
from datetime import timedelta
from home.models.FailedLoginAttempt import FailedLoginAttempt
from home.service.FailedLoginAttemptService import FailedLoginAttemptService

class FailedLoginAttemptServiceTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.META['REMOTE_ADDR'] = '192.168.1.1'
        self.username = 'testuser'
        self.service = FailedLoginAttemptService(self.request, self.username)

    def test_add_or_create_failed_login_attempt_new(self):
        # Test creating a new failed login attempt
        self.service.add_or_create_failed_login_attempt()
        failed_attempt = FailedLoginAttempt.objects.get(ip_address='192.168.1.1', username='testuser')
        self.assertEqual(failed_attempt.attempts, 1)
        self.assertAlmostEqual(failed_attempt.timestamp, self.service.now, delta=timedelta(seconds=1))

    def test_add_or_create_failed_login_attempt_existing(self):
        # Test updating an existing failed login attempt within the time threshold
        FailedLoginAttempt.objects.create(ip_address='192.168.1.1', username='testuser', timestamp=timezone.now())
        self.service.add_or_create_failed_login_attempt()
        failed_attempt = FailedLoginAttempt.objects.get(ip_address='192.168.1.1', username='testuser')
        self.assertEqual(failed_attempt.attempts, 2)

    def test_add_or_create_failed_login_attempt_timeout(self):
        # Test updating an existing failed login attempt outside the time threshold
        old_time = timezone.now() - timedelta(minutes=20)
        FailedLoginAttempt.objects.create(ip_address='192.168.1.1', username='testuser', timestamp=old_time, attempts=3)
        self.service.add_or_create_failed_login_attempt()
        failed_attempt = FailedLoginAttempt.objects.get(ip_address='192.168.1.1', username='testuser')
        self.assertEqual(failed_attempt.attempts, 1)

    def test_purge(self):
        # Test purging failed login attempts
        FailedLoginAttempt.objects.create(ip_address='192.168.1.1', username='testuser')
        self.service.purge()
        self.assertFalse(FailedLoginAttempt.objects.filter(ip_address='192.168.1.1', username='testuser').exists())

    def test_is_timeout_false(self):
        # Test is_timeout when attempts are less than or equal to 3
        FailedLoginAttempt.objects.create(ip_address='192.168.1.1', username='testuser', attempts=3)
        self.assertFalse(self.service.is_timeout())

    def test_is_timeout_true(self):
        # Test is_timeout when attempts are greater than 3
        FailedLoginAttempt.objects.create(ip_address='192.168.1.1', username='testuser', attempts=4)
        self.assertTrue(self.service.is_timeout())