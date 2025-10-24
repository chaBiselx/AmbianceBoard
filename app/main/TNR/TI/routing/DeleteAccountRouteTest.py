"""
Test d'intégration pour la route: delete account (/account/settings/delete-account)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class DeleteAccountRouteTest(TestCase):
    """Tests pour la route delete account"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_deleteaccount_accessible_when_authenticated(self):
        """Test que la route delete account est accessible pour un utilisateur authentifié"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('deleteAccount'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_deleteaccount_requires_auth(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(reverse('deleteAccount'))
        self.assertIn(response.status_code, [302, 401, 403])

