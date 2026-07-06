"""
Test d'integration pour la route: support (/support)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse


@tag('integration')
class SupportContactRouteTest(TestCase):
    """Tests pour la route support contact"""

    def setUp(self):
        self.client = Client()

    def test_support_contact_accessible_without_auth(self):
        response = self.client.get(reverse('supportContact'))
        self.assertEqual(response.status_code, 200)

    def test_support_contact_returns_html(self):
        response = self.client.get(reverse('supportContact'))
        self.assertIn('text/html', response.get('Content-Type', ''))
