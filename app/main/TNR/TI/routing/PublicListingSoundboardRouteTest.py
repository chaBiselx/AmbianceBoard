"""
Test d'intégration pour la route: public soundboards listing (/public/soundboards)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class PublicListingSoundboardRouteTest(TestCase):
    """Tests pour la route public soundboards listing"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
    
    def test_publiclistingsoundboard_accessible_without_auth(self):
        """Test que la route public soundboards listing est accessible sans authentification"""
        response = self.client.get(reverse('publicListingSoundboard'))
        self.assertEqual(response.status_code, 200)
    
