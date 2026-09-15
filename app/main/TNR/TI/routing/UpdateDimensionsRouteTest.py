"""
Test d'intégration pour la route: update dimensions (/account/settings/dimensions)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class UpdateDimensionsRouteTest(TestCase):
    """Tests pour la route update dimensions"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )  # NOSONAR

    def test_updatedimensions_accessible_when_authenticated(self):
        """Test que la route update dimensions est accessible pour un utilisateur authentifié"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('updateDimensions'))
        self.assertEqual(response.status_code, 200)

    def test_updatedimensions_requires_auth(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(reverse('updateDimensions'))
        self.assertIn(response.status_code, [302, 401, 403])
