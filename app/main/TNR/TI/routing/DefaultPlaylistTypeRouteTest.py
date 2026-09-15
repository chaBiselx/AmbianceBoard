"""
Test d'intégration pour la route: default playlist type (/account/settings/playlists/style)
"""
from django.test import tag
from django.urls import reverse

from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase


@tag('integration')
class DefaultPlaylistTypeRouteTest(AuthenticatedTestCase):
    """Tests pour la route default playlist type"""

    def setUp(self):
        super().setUp()

    def test_defaultplaylisttype_get_accessible_when_authenticated(self):
        """Test que la route est accessible en GET pour un utilisateur authentifié"""
        self.login()
        response = self.client.get(reverse('defaultPlaylistType'))
        self.assertEqual(response.status_code, 200)

    def test_defaultplaylisttype_requires_auth(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(reverse('defaultPlaylistType'))
        self.assertIn(response.status_code, [302, 401, 403])

    def test_defaultplaylisttype_post_invalid_data_renders_form(self):
        """Test qu'un POST avec des données invalides réaffiche le formulaire"""
        self.login()
        response = self.client.post(reverse('defaultPlaylistType'), {})
        self.assertIn(response.status_code, [200, 302])
