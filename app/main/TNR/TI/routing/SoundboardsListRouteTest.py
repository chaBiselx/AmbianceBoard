"""
Test d'intégration pour la route: soundboards list (/soundBoards/)
"""
from django.test import tag
from django.urls import reverse

from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase


@tag('integration')
class SoundboardsListRouteTest(AuthenticatedTestCase):
    """Tests pour la route soundboards list"""
    
    def setUp(self):
        super().setUp()
    
    def test_soundboardslist_accessible_when_authenticated(self):
        """Test que la route soundboards list est accessible pour un utilisateur authentifié"""
        self.login()
        response = self.client.get(reverse('soundboardsList'))
        self.assertEqual(response.status_code, 200)
    
    def test_soundboardslist_requires_auth(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(reverse('soundboardsList'))
        self.assertIn(response.status_code, [302, 401, 403])

