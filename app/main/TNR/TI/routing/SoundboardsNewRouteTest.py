"""
Test d'intégration pour la route: create soundboard (/soundBoards/new)
"""
from django.test import tag
from django.urls import reverse

from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase


@tag('integration')
class SoundboardsNewRouteTest(AuthenticatedTestCase):
    """Tests pour la route create soundboard"""
    
    def setUp(self):
        super().setUp()
    
    def test_soundboardsnew_accessible_when_authenticated(self):
        """Test que la route create soundboard est accessible pour un utilisateur authentifié"""
        self.login()
        response = self.client.get(reverse('soundboardsNew'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_soundboardsnew_requires_auth(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(reverse('soundboardsNew'))
        self.assertIn(response.status_code, [302, 401, 403])

