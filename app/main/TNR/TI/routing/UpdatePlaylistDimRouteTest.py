"""
Test d'intégration pour la route: update playlist dim (/account/settings/playlists/dimension)
"""
import json
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class UpdatePlaylistDimRouteTest(TestCase):
    """Tests pour la route update playlist dim"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )  # NOSONAR

    def test_updateplaylistdim_accessible_when_authenticated(self):
        """Test que la route est accessible pour un utilisateur authentifié"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('updatePlaylistDim')
        response = self.client.generic('UPDATE', url, data=json.dumps({'dim': '50'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), 'Dimensions updated successfully.')

    def test_updateplaylistdim_requires_auth(self):
        """Test que la route nécessite une authentification"""
        url = reverse('updatePlaylistDim')
        response = self.client.generic('UPDATE', url, data=json.dumps({'dim': '50'}), content_type='application/json')
        self.assertIn(response.status_code, [302, 401, 403])

    def test_updateplaylistdim_missing_dim_returns_error(self):
        """Test qu'une requête sans le champ dim renvoie une erreur"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('updatePlaylistDim')
        response = self.client.generic('UPDATE', url, data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 500)
