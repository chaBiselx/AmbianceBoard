"""
Test d'intégration pour la route: sitemap.xml (/sitemap.xml)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class SitemapXmlRouteTest(TestCase):
    """Tests pour la route sitemap.xml"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
    
    def test_sitemap_xml_accessible_without_auth(self):
        """Test que la route sitemap.xml est accessible sans authentification"""
        response = self.client.get(reverse('sitemap_xml'))
        self.assertEqual(response.status_code, 200)
    
    def test_sitemap_xml_content_type(self):
        """Test que la route retourne le bon content-type"""
        response = self.client.get(reverse('sitemap_xml'))
        self.assertEqual(response.get('Content-Type'), 'application/xml')

