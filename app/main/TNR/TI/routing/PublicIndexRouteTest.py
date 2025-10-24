"""
Test d'intégration pour la route: public index (/public/)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class PublicIndexRouteTest(TestCase):
    """Tests pour la route public index"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
    
    def test_publicindex_accessible_without_auth(self):
        """Test que la route public index est accessible sans authentification"""
        response = self.client.get(reverse('publicIndex'))
        self.assertIn(response.status_code, [200, 302])
    
