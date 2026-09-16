"""
Tests d'intégration pour les routes manager user tiers (/manager/user-tiers/*)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


@tag('integration')
class ManagerUserTierRouteTest(TestCase):
    """Tests pour les routes de gestion des tiers d'utilisateurs"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        role_group, _ = Group.objects.get_or_create(name='ROLE_ADMIN')
        self.user.groups.add(role_group)
        self.other_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='normalpass123'
        )
        self.target_user = User.objects.create_user(
            username='targetuser',
            email='target@example.com',
            password='targetpass123'
        )

    def test_adminusertiersdashboard_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('adminUserTiersDashboard'))
        self.assertIn(response.status_code, [200, 302])

    def test_adminusertiersdashboard_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('adminUserTiersDashboard'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_adminusertierslisting_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('adminUserTiersListing'), {'page': 1, 'search': '', 'tier': ''})
        self.assertIn(response.status_code, [200, 302])

    def test_adminusertierslisting_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('adminUserTiersListing'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_adminusertieredit_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('adminUserTierEdit', kwargs={'user_uuid': self.target_user.uuid}))
        self.assertIn(response.status_code, [200, 302])

    def test_adminusertieredit_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('adminUserTierEdit', kwargs={'user_uuid': self.target_user.uuid}))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_managerusertierbulkaction_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('managerUserTierBulkAction'), {
            'action': 'extend_subscription',
            'user_ids': [str(self.target_user.id)],
            'extend_days': '30',
        })
        self.assertIn(response.status_code, [200, 302])

    def test_managerusertierbulkaction_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.post(reverse('managerUserTierBulkAction'), {
            'action': 'extend_subscription',
            'user_ids': [str(self.target_user.id)],
            'extend_days': '30',
        })
        self.assertIn(response.status_code, [302, 403, 404])

    def test_managerusertiersexpiring_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerUserTiersExpiring'), {'page': 1, 'days': 7})
        self.assertIn(response.status_code, [200, 302])

    def test_managerusertiersexpiring_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerUserTiersExpiring'))
        self.assertIn(response.status_code, [302, 403, 404])
