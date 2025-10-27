from django.test import TestCase, tag
from django.http import HttpResponseRedirect
from django.conf import settings
from unittest.mock import patch
from urllib.parse import urlparse

from main.domain.common.utils.url import redirection_url


# Tests d'intégration avec différents scénarios
@tag('integration')
class RedirectionUrlIntegrationTestCase(TestCase):
    
    def setUp(self):
        """Configuration initiale pour les tests d'intégration"""
        # Sauvegarde des settings originaux
        self.original_scheme = getattr(settings, 'APP_SCHEME', None)
        self.original_host = getattr(settings, 'APP_HOST', None)
        self.original_port = getattr(settings, 'APP_PORT', None)
    
    def tearDown(self):
        """Restauration des settings originaux après chaque test"""
        if self.original_scheme is not None:
            settings.APP_SCHEME = self.original_scheme
        else:
            delattr(settings, 'APP_SCHEME')
        if self.original_host is not None:
            settings.APP_HOST = self.original_host
        else:
            delattr(settings, 'APP_HOST')
        if self.original_port is not None:
            settings.APP_PORT = self.original_port
        else:
            delattr(settings, 'APP_PORT')
    
    def test_common_scenarios(self):
        """Test de scénarios courants d'utilisation"""
        # Configuration pour un environnement de développement
        settings.APP_SCHEME = 'http'
        settings.APP_HOST = 'localhost'
        settings.APP_PORT = 8000
        test_cases = [
            # (url_input, expected_result)
            
            ('http://localhost:8000/admin/', 'http://localhost:8000'),
            ('http://localhost:8000/', 'http://localhost:8000'),
            ('http://localhost:9000/', '/'),  # Mauvais port
            ('http://127.0.0.1:8000/', '/'),  # Mauvais host
            ('https://localhost:8000/', '/'),  # Bon host:port mais mauvais scheme dans l'URL
            ('http://evil.com/', '/'),  # Domaine malveillant
            ('/admin/', '/admin/'),  # relative url
            ('/admin?param=value', '/admin?param=value'),  # relative url avec paramètres
        ]
        
        for url_input, expected_url in test_cases:
            with self.subTest(url=url_input):
                result = redirection_url(url_input)
                self.assertEqual(result, expected_url, 
                               f"Failed for URL: {url_input}")