"""
Test d'intégration pour la route: manager dashboard (/manager/)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


@tag('integration')
class ManagerDashboardRouteTest(TestCase):
    """Tests pour la route manager dashboard"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        role_group, _ = Group.objects.get_or_create(name='ROLE_ADMIN')
        self.user.groups.add(role_group)
    
    def test_managerdashboard_accessible_when_authenticated(self):
        """Test que la route manager dashboard est accessible pour un utilisateur avec le rôle ROLE_ADMIN"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerDashboard'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_managerdashboard_requires_role(self):
        """Test que la route nécessite le rôle ROLE_ADMIN"""
        # Utilisateur sans le rôle
        _ = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='normalpass123'
        )
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerDashboard'))
        self.assertIn(response.status_code, [302, 403, 404])

