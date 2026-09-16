"""
Tests d'intégration pour la route manager d'envoi d'email (/manager/send-email/)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


@tag('integration')
class ManagerSendEmailRouteTest(TestCase):
    """Tests pour la route d'envoi d'email manager"""

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

    def test_managersendemail_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerSendEmail'))
        self.assertIn(response.status_code, [200, 302])

    def test_managersendemail_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerSendEmail'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_managersendemail_post_external_email_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('managerSendEmail'), {
            'subject': 'Subject',
            'message': 'Message body',
            'external_emails': 'someone@example.com',
        })
        self.assertIn(response.status_code, [200, 302])
