"""
Test d'integration pour la route: support (/support)
"""
from time import time
from unittest.mock import patch

from django.core.cache import cache
from django.core.signing import TimestampSigner
from django.test import TestCase, Client, tag
from django.urls import reverse
from main.domain.general.helper.TimestampToken import TimestampToken


@tag('integration')
class SupportContactRouteTest(TestCase):
    """Tests pour la route support contact"""

    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_support_contact_accessible_without_auth(self):
        response = self.client.get(reverse('supportContact'))
        self.assertEqual(response.status_code, 200)

    def test_support_contact_returns_html(self):
        response = self.client.get(reverse('supportContact'))
        self.assertIn('text/html', response.get('Content-Type', ''))

    @patch('main.interface.ui.controller.general.generalViews.SupportContactService.send')
    def test_support_contact_does_not_send_when_honeypot_is_filled(self, send_mock):
        response = self.client.post(reverse('supportContact'), {
            'website': 'https://spam.example',
            'email': 'sender@example.com',
            'subject': 'Support request',
            'message': 'Please help.',
            'support_form_token': self._create_token(age_seconds=10),
        })

        self.assertEqual(response.status_code, 302)
        send_mock.assert_not_called()

    @patch('main.interface.ui.controller.general.generalViews.SupportContactService.send')
    def test_support_contact_does_not_send_when_submitted_too_fast(self, send_mock):
        response = self.client.post(reverse('supportContact'), {
            'website': '',
            'email': 'sender@example.com',
            'subject': 'Support request',
            'message': 'Please help.',
            'support_form_token': self._create_token(age_seconds=0),
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].non_field_errors())
        send_mock.assert_not_called()

    @patch('main.interface.ui.controller.general.generalViews.SupportContactService.send')
    def test_support_contact_sends_after_minimum_fill_time(self, send_mock):
        response = self.client.post(reverse('supportContact'), {
            'website': '',
            'email': 'sender@example.com',
            'subject': 'Support request',
            'message': 'Please help.',
            'support_form_token': self._create_token(age_seconds=10),
        })

        self.assertEqual(response.status_code, 302)
        send_mock.assert_called_once()

    @staticmethod
    def _create_token(age_seconds):
        started_at = int(time()) - age_seconds
        return TimestampSigner(
            salt=TimestampToken.SUPPORT_CONTACT_TOKEN_SALT
        ).sign(str(started_at))
