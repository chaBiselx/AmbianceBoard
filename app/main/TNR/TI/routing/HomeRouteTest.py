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

    def test_home_renders_french_copy(self):
        response = self.client.get(reverse('home'), HTTP_ACCEPT_LANGUAGE='fr-FR,fr;q=0.9')

        self.assertContains(response, 'Donnez vie à vos parties.')
        self.assertContains(response, 'Essayez une ambiance')

    def test_home_renders_english_copy(self):
        response = self.client.get(reverse('home'), HTTP_ACCEPT_LANGUAGE='en-US,en;q=0.9')

        self.assertContains(response, 'Bring your adventures to life.')
        self.assertContains(response, 'Try a soundscape')
