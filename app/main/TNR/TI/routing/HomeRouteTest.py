"""
Test d'intégration pour la route: home (/)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse


@tag('integration')
class HomeRouteTest(TestCase):
    """Tests pour la route home"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
    
    def test_home_accessible_without_auth(self):
        """Test que la page home est accessible sans authentification"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_home_returns_html(self):
        """Test que la route home retourne du HTML"""
        response = self.client.get(reverse('home'))
        self.assertIn('text/html', response.get('Content-Type', ''))
