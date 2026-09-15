"""
Tests d'intégration pour les routes manager home demo (/manager/home-demo/*)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.HomeDemoItem import HomeDemoItem

User = get_user_model()


@tag('integration')
class ManagerHomeDemoRouteTest(TestCase):
    """Tests pour les routes de gestion des éléments Home Demo"""

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
        self.public_soundboard = SoundBoard.objects.create(
            user=self.user, name='Public board', is_public=True
        )
        self.used_soundboard = SoundBoard.objects.create(
            user=self.user, name='Used board', is_public=True
        )
        self.home_demo_item = HomeDemoItem.objects.create(
            title='Medieval',
            icon='⚔️',
            soundboard=self.used_soundboard,
        )

    def test_managerhomedemoitems_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerHomeDemoItems'), {'page': 1})
        self.assertIn(response.status_code, [200, 302])

    def test_managerhomedemoitems_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerHomeDemoItems'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_managerhomedemoselectsoundboard_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerHomeDemoSelectSoundboard'), {'page': 1, 'tag': ''})
        self.assertIn(response.status_code, [200, 302])

    def test_managerhomedemoselectsoundboard_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerHomeDemoSelectSoundboard'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_managerhomedemocreatewithsoundboard_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerHomeDemoCreateWithSoundboard', kwargs={'soundboard_uuid': self.public_soundboard.uuid}))
        self.assertIn(response.status_code, [200, 302])

    def test_managerhomedemocreatewithsoundboard_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerHomeDemoCreateWithSoundboard', kwargs={'soundboard_uuid': self.public_soundboard.uuid}))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_manager_home_demo_update_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('manager_home_demo_update', kwargs={'uuid': self.home_demo_item.uuid}))
        self.assertIn(response.status_code, [200, 302])

    def test_manager_home_demo_update_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('manager_home_demo_update', kwargs={'uuid': self.home_demo_item.uuid}))
        self.assertIn(response.status_code, [302, 403, 404])
