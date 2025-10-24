"""
Test d'intégration pour la route: create playlist (/playlist/create)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class AddPlaylistRouteTest(TestCase):
    """Tests pour la route create playlist"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_addplaylist_accessible_when_authenticated(self):
        """Test que la route create playlist est accessible pour un utilisateur authentifié"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('addPlaylist'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_addplaylist_requires_auth(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(reverse('addPlaylist'))
        self.assertIn(response.status_code, [302, 401, 403])

