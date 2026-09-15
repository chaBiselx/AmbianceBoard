"""
Test d'intégration pour la route: create playlist (/playlist/create)
"""
from django.test import tag
from django.urls import reverse

from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase


@tag('integration')
class AddPlaylistRouteTest(AuthenticatedTestCase):
    """Tests pour la route create playlist"""
    
    def setUp(self):
        super().setUp()
    
    def test_addplaylist_accessible_when_authenticated(self):
        """Test que la route create playlist est accessible pour un utilisateur authentifié"""
        self.login()
        response = self.client.get(reverse('addPlaylist'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_addplaylist_requires_auth(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(reverse('addPlaylist'))
        self.assertIn(response.status_code, [302, 401, 403])

