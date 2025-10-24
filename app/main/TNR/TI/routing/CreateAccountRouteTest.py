"""
Test d'intégration pour la route: create account (/create-account/)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class CreateAccountRouteTest(TestCase):
    """Tests pour la route create account"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
    
    def test_createaccount_accessible_without_auth(self):
        """Test que la route create account est accessible sans authentification"""
        response = self.client.get(reverse('createAccount'))
        self.assertEqual(response.status_code, 200)
    
