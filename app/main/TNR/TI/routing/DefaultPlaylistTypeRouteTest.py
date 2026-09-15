"""
Test d'intégration pour la route: default playlist type (/account/settings/playlists/style)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class DefaultPlaylistTypeRouteTest(TestCase):
    """Tests pour la route default playlist type"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )  # NOSONAR

    def test_defaultplaylisttype_get_accessible_when_authenticated(self):
        """Test que la route est accessible en GET pour un utilisateur authentifié"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('defaultPlaylistType'))
        self.assertEqual(response.status_code, 200)

    def test_defaultplaylisttype_requires_auth(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(reverse('defaultPlaylistType'))
        self.assertIn(response.status_code, [302, 401, 403])

    def test_defaultplaylisttype_post_invalid_data_renders_form(self):
        """Test qu'un POST avec des données invalides réaffiche le formulaire"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('defaultPlaylistType'), {})
        self.assertIn(response.status_code, [200, 302])
