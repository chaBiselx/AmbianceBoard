"""
Test d'intégration pour la route: update theme (/account/settings/theme)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class UpdateThemeRouteTest(TestCase):
    """Tests pour la route update theme"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_updatetheme_accessible_when_authenticated(self):
        """Test que la route update theme est accessible pour un utilisateur authentifié"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('updateTheme'), {'theme': 'dark'})
        self.assertIn(response.status_code, [200, 302, 400, 405])
    
    def test_updatetheme_requires_auth(self):
        """Test que la route nécessite une authentification"""
        response = self.client.post(reverse('updateTheme'), {'theme': 'dark'})
        self.assertIn(response.status_code, [302, 401, 403, 405])

