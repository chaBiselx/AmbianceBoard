"""
Test d'intégration pour la route: faq (/faq)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse


@tag('integration')
class FaqRouteTest(TestCase):
    """Tests pour la route faq"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()

    def test_faq_accessible_without_auth(self):
        """Test que la route faq est accessible sans authentification"""
        response = self.client.get(reverse('faq'))
        self.assertEqual(response.status_code, 200)

    def test_faq_renders_expected_template(self):
        """Test que la route faq utilise le bon template"""
        response = self.client.get(reverse('faq'))
        self.assertTemplateUsed(response, 'Html/General/faq.html')
