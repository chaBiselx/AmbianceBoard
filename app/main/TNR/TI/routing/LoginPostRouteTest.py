"""
Test d'intégration pour la route: login POST (/login/post)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class LoginPostRouteTest(TestCase):
    """Tests pour la route login POST"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
    
    def test_loginpost_accessible_without_auth(self):
        """Test que la route login POST est accessible sans authentification"""
        response = self.client.post(reverse('loginPost'), {
            'identifiant': 'testuser',
            'password': 'testpass'
        })
        self.assertIn(response.status_code, [200, 302, 400])
    
