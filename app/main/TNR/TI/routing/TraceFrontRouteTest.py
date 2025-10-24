"""
Test d'intégration pour la route: trace front (/trace-front)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class TraceFrontRouteTest(TestCase):
    """Tests pour la route trace front"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
    
    def test_tracefront_accessible_without_auth(self):
        """Test que la route trace front est accessible sans authentification"""
        response = self.client.get(reverse('traceFront'))
        self.assertIn(response.status_code, [200, 400, 405])
    
