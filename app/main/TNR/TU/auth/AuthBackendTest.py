from django.test import TestCase, tag
from django.contrib.auth import get_user_model
from main.application.auth.UsernameOrEmailBackend import UsernameOrEmailBackend

User = get_user_model()

@tag('unitaire')
class AuthBackendTest(TestCase):
    def setUp(self):
        self.backend = UsernameOrEmailBackend()
        self.user_email = User.objects.create_user(username='user1', email='johnDoe@example.com', password='pass1234') # NOSONAR
        self.user_username_only = User.objects.create_user(username='user2', email='user2@example.com', password='pass1234') # NOSONAR
        self.user_inactive = User.objects.create_user(username='user3', email='user3@example.com', password='pass1234', is_active=False) # NOSONAR

    def test_authenticate_with_email_success(self):
        user = self.backend.authenticate(None, username='johnDoe@example.com', password='pass1234') # NOSONAR
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.user_email.pk)

    def test_authenticate_with_username_success(self):
        user = self.backend.authenticate(None, username='user2', password='pass1234') # NOSONAR
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.user_username_only.pk)

    def test_authenticate_wrong_password(self):
        user = self.backend.authenticate(None, username='johnDoe@example.com', password='wrong') # NOSONAR
        self.assertIsNone(user)

    def test_authenticate_user_not_found(self):
        user = self.backend.authenticate(None, username='unknown@example.com', password='pass1234') # NOSONAR
        self.assertIsNone(user)

    def test_authenticate_inactive_user(self):
        # ModelBackend user_can_authenticate renverra False si is_active=False
        user = self.backend.authenticate(None, username='user3', password='pass1234') # NOSONAR
        self.assertIsNone(user)
