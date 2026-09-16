"""
Tests d'intégration pour les routes de dashboards JSON manager (/manager/dashboard/*)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


@tag('integration')
class ManagerActivityDashboardsRouteTest(TestCase):
    """Tests pour les routes de dashboards d'activité manager"""

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

    def test_manageruseraccountdashboard_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerUserAccountDashboard'), {'period': 30})
        self.assertIn(response.status_code, [200, 302])

    def test_manageruseraccountdashboard_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerUserAccountDashboard'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_managerusersactivitydashboard_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerUsersActivityDashboard'), {'period': 30})
        self.assertIn(response.status_code, [200, 302])

    def test_managerusersactivitydashboard_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerUsersActivityDashboard'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_managererroractivitydashboard_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerErrorActivityDashboard'), {'period': 30})
        self.assertIn(response.status_code, [200, 302])

    def test_managererroractivitydashboard_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerErrorActivityDashboard'))
        self.assertIn(response.status_code, [302, 403, 404])
