from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, tag
from django.urls import reverse

User = get_user_model()


@tag('integration')
class DebugEmailTestRouteTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='debug-email-user',
            email='debug-email-user@test.com',
            password='password123',
        )

    def test_debug_email_page_is_accessible(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('debugEmailTest'))

        self.assertEqual(response.status_code, 200)

    @patch('main.interface.ui.controller.debug.debugEmailViews.EmailSender')
    def test_debug_email_send_all_dispatches_every_message(self, mock_email_sender):
        self.client.force_login(self.user)
        mock_mailer = MagicMock()
        mock_email_sender.return_value = mock_mailer

        response = self.client.post(reverse('debugEmailTest'), {'action': 'all'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_mailer.send_email.call_count, 12)