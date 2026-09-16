"""
Tests d'intégration pour les routes manager cron (/manager/cron/*)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


@tag('integration')
class ManagerCronViewsRouteTest(TestCase):
    """Tests pour les routes de gestion des tâches planifiées"""

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

    def test_managercronviews_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerCronViews'))
        self.assertIn(response.status_code, [200, 302])

    def test_managercronviews_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerCronViews'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_admincleanmediafolders_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('adminCleanMediaFolders'))
        self.assertIn(response.status_code, [200, 302])

    def test_admincleanmediafolders_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('adminCleanMediaFolders'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_managerexpireusertiers_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerExpireUserTiers'))
        self.assertIn(response.status_code, [200, 302])

    def test_managerexpireusertiers_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerExpireUserTiers'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_managersyncdomainblacklist_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerSyncDomainBlacklist'))
        self.assertIn(response.status_code, [200, 302])

    def test_managersyncdomainblacklist_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerSyncDomainBlacklist'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_managerpurgeexpiredsharedsoundboard_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerPurgeExpiredSharedSoundboard'))
        self.assertIn(response.status_code, [200, 302])

    def test_managerpurgeexpiredsharedsoundboard_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerPurgeExpiredSharedSoundboard'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_managerpurgeoluseractivity_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerPurgeOldUserActivity'))
        self.assertIn(response.status_code, [200, 302])

    def test_managerpurgeoluseractivity_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerPurgeOldUserActivity'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_managermusiclabelercronservice_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerMusicLabelerCronService'))
        self.assertIn(response.status_code, [200, 302])

    def test_managermusiclabelercronservice_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerMusicLabelerCronService'))
        self.assertIn(response.status_code, [302, 403, 404])
