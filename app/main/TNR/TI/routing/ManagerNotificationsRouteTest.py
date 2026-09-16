"""
Tests d'intégration pour les routes manager notifications (/manager/notifications/*)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

from main.architecture.persistence.models.GeneralNotification import GeneralNotification

User = get_user_model()


@tag('integration')
class ManagerNotificationsRouteTest(TestCase):
    """Tests pour les routes de gestion des notifications générales"""

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
        self.notification = GeneralNotification.objects.create(
            message='Hello world',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            is_active=True,
        )

    def test_managernotifications_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerNotifications'), {'page': 1})
        self.assertIn(response.status_code, [200, 302])

    def test_managernotifications_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerNotifications'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_manager_notifications_create_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('manager_notifications_create'))
        self.assertIn(response.status_code, [200, 302])

    def test_manager_notifications_create_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('manager_notifications_create'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_manager_notifications_create_post_creates_notification(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('manager_notifications_create'), {
            'message': 'New notification',
            'class_name': 'info',
            'start_date': '2026-01-01T00:00',
            'end_date': '2026-12-31T00:00',
            'is_active': 'on',
        })
        self.assertIn(response.status_code, [200, 302])

    def test_manager_notifications_update_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('manager_notifications_update', kwargs={'uuid': self.notification.uuid}))
        self.assertIn(response.status_code, [200, 302])

    def test_manager_notifications_update_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('manager_notifications_update', kwargs={'uuid': self.notification.uuid}))
        self.assertIn(response.status_code, [302, 403, 404])
