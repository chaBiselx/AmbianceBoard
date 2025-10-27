"""
Test d'intégration pour la route: robots.txt (/robots.txt)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class RobotsTxtRouteTest(TestCase):
    """Tests pour la route robots.txt"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
    
    def test_robots_txt_accessible_without_auth(self):
        """Test que la route robots.txt est accessible sans authentification"""
        response = self.client.get(reverse('robots_txt'))
        self.assertEqual(response.status_code, 200)
    
    def test_robots_txt_content_type(self):
        """Test que la route retourne le bon content-type"""
        response = self.client.get(reverse('robots_txt'))
        self.assertEqual(response.get('Content-Type'), 'text/plain')

