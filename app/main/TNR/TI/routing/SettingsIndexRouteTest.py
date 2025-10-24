"""
Test d'intégration pour la route: settings index (/account/settings/)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class SettingsIndexRouteTest(TestCase):
    """Tests pour la route settings index"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_settingsindex_accessible_when_authenticated(self):
        """Test que la route settings index est accessible pour un utilisateur authentifié"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('settingsIndex'))
        self.assertEqual(response.status_code, 200)
    
    def test_settingsindex_requires_auth(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(reverse('settingsIndex'))
        self.assertIn(response.status_code, [302, 401, 403])

