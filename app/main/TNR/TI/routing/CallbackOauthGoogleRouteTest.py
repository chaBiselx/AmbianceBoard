"""
Test d'intégration pour la route: callback oauth google (/accounts/profile/)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse


@tag('integration')
class CallbackOauthGoogleRouteTest(TestCase):
    """Tests pour la route callback oauth google"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()

    def test_callback_oauth_google_redirects_to_home(self):
        """Test que la route redirige vers la page d'accueil"""
        response = self.client.get(reverse('callback_oauth_google'))
        self.assertRedirects(response, reverse('home'))

    def test_callback_oauth_google_accessible_without_auth(self):
        """Test que la route est accessible sans authentification"""
        response = self.client.get(reverse('callback_oauth_google'))
        self.assertEqual(response.status_code, 302)
