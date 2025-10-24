"""
Test d'intégration pour la route: legal-notice (/legal-notice)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse


@tag('integration')
class LegalNoticeRouteTest(TestCase):
    """Tests pour la route legal notice"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
    
    def test_legal_notice_accessible_without_auth(self):
        """Test que la page legal notice est accessible sans authentification"""
        response = self.client.get(reverse('legalNotice'))
        self.assertEqual(response.status_code, 200)
    
    def test_legal_notice_returns_html(self):
        """Test que la route legal notice retourne du HTML"""
        response = self.client.get(reverse('legalNotice'))
        self.assertIn('text/html', response.get('Content-Type', ''))
