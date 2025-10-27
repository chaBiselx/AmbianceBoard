"""
Test d'intégration pour la route: pricing (/pricing)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse


@tag('integration')
class PricingRouteTest(TestCase):
    """Tests pour la route pricing"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
    
    def test_pricing_accessible_without_auth(self):
        """Test que la page pricing est accessible sans authentification"""
        response = self.client.get(reverse('pricing'))
        self.assertEqual(response.status_code, 200)
    
    def test_pricing_returns_html(self):
        """Test que la route pricing retourne du HTML"""
        response = self.client.get(reverse('pricing'))
        self.assertIn('text/html', response.get('Content-Type', ''))
