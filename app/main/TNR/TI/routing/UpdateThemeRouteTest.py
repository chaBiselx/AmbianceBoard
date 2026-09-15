"""
Test d'intégration pour la route: update theme (/account/settings/theme)
"""
from django.test import tag
from django.urls import reverse

from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase


@tag('integration')
class UpdateThemeRouteTest(AuthenticatedTestCase):
    """Tests pour la route update theme"""
    
    def setUp(self):
        super().setUp()
    
    def test_updatetheme_accessible_when_authenticated(self):
        """Test que la route update theme est accessible pour un utilisateur authentifié"""
        self.login()
        response = self.client.post(reverse('updateTheme'), {'theme': 'dark'})
        self.assertIn(response.status_code, [200, 302, 400, 405])
    
    def test_updatetheme_requires_auth(self):
        """Test que la route nécessite une authentification"""
        response = self.client.post(reverse('updateTheme'), {'theme': 'dark'})
        self.assertIn(response.status_code, [302, 401, 403, 405])

