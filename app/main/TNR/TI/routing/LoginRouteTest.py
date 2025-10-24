"""
Test d'intégration pour la route: login page (/login/)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class LoginRouteTest(TestCase):
    """Tests pour la route login page"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
    
    def test_login_accessible_without_auth(self):
        """Test que la route login page est accessible sans authentification"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
