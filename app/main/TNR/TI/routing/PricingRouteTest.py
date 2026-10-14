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

    def test_pricing_has_seo_metadata_disclosing_unavailable_prices(self):
        """Les metadonnees SEO du pricing precisent que les tarifs ne sont pas etablis."""
        response = self.client.get(reverse('pricing'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<title>Tarifs AmbianceBoard — Formules soundboard JDR | AmbianceBoard</title>', html=False)
        self.assertContains(
            response,
            '<meta name="description" content="Les tarifs des formules AmbianceBoard ne sont pas encore en place. Découvrez les offres et leurs fonctionnalités ; les prix seront annoncés lorsqu&#x27;ils seront définis."',
            html=False,
        )
        self.assertContains(response, '<link rel="canonical" href="http://testserver/pricing"', html=False)
        self.assertContains(response, '"@type": "WebPage"', html=False)
        self.assertNotContains(response, '"@type": "Offer"', html=False)

    def test_pricing_is_in_sitemap(self):
        """La page de tarifs publique figure dans le sitemap."""
        response = self.client.get(reverse('sitemap_xml'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<loc>http://testserver/pricing</loc>', html=False)
