"""
Test d'intégration pour la route: settings index (/account/settings/)
"""
from django.test import tag
from django.urls import reverse

from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase


@tag('integration')
class SettingsIndexRouteTest(AuthenticatedTestCase):
    """Tests pour la route settings index"""
    
    def setUp(self):
        super().setUp()
    
    def test_settingsindex_accessible_when_authenticated(self):
        """Test que la route settings index est accessible pour un utilisateur authentifié"""
        self.login()
        response = self.client.get(reverse('settingsIndex'))
        self.assertEqual(response.status_code, 200)
    
    def test_settingsindex_requires_auth(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(reverse('settingsIndex'))
        self.assertIn(response.status_code, [302, 401, 403])

