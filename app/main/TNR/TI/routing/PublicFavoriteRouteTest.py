"""
Test d'intégration pour la route: Favoris publics (/public/favorite)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class PublicFavoriteRouteTest(TestCase):
    """Tests pour la route des favoris publics"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_public_favorite_accessible_without_auth(self):
        """Test que la route est accessible sans authentification"""
        response = self.client.get(reverse('publicFavorite'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_public_favorite_accessible_when_authenticated(self):
        """Test que la route est accessible quand authentifié"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('publicFavorite'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_public_favorite_post_method(self):
        """Test la méthode POST si supportée"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('publicFavorite'), {})
        self.assertIn(response.status_code, [200, 302, 400, 405])
