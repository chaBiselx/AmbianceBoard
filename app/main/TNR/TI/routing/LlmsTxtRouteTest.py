"""
Test d'intégration pour la route: llms.txt (/llms.txt)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse


@tag('integration')
class LlmsTxtRouteTest(TestCase):
    """Tests pour la route llms.txt"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()

    def test_llms_txt_accessible_without_auth(self):
        """Test que la route llms.txt est accessible sans authentification"""
        response = self.client.get(reverse('llms_txt'))
        self.assertEqual(response.status_code, 200)

    def test_llms_txt_content_type(self):
        """Test que la route retourne le bon content-type"""
        response = self.client.get(reverse('llms_txt'))
        self.assertEqual(response.get('Content-Type'), 'text/plain')
