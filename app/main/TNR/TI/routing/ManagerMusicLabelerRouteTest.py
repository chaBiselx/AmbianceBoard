"""
Tests d'intégration pour les routes manager music labeler (/manager/music-labeler/*)
"""
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


@tag('integration')
class ManagerMusicLabelerRouteTest(TestCase):
    """Tests pour les routes du music labeler IA manager"""

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

    def test_managermusiclabeler_accessible_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerMusicLabeler'), {'page': 1})
        self.assertIn(response.status_code, [200, 302])

    def test_managermusiclabeler_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerMusicLabeler'))
        self.assertIn(response.status_code, [302, 403, 404])

    @patch('main.interface.ui.controller.manager.managerMusicLabelerViews.MusicLabelerService')
    def test_managermusiclabeleranalyze_accessible_when_authenticated(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service.analyze_by_id.return_value = {'categories': {}}
        mock_service_cls.return_value = mock_service

        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('managerMusicLabelerAnalyze', kwargs={'music_id': 1}))
        self.assertIn(response.status_code, [200, 302])

    def test_managermusiclabeleranalyze_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.post(reverse('managerMusicLabelerAnalyze', kwargs={'music_id': 1}))
        self.assertIn(response.status_code, [302, 403, 404])

    @patch('main.interface.ui.controller.manager.managerMusicLabelerViews.os.path.exists', return_value=True)
    @patch('main.interface.ui.controller.manager.managerMusicLabelerViews.Music')
    def test_managermusiclabelerstream_accessible_when_authenticated(self, mock_music_cls, mock_path_exists):
        mock_music = MagicMock()
        mock_music.file.path = '/fake/path/audio.mp3'
        mock_music.get_reponse_content.return_value = HttpResponse(b'audio-bytes', content_type='audio/mpeg')
        mock_music_cls.objects.get.return_value = mock_music

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerMusicLabelerStream', kwargs={'music_id': 1}))
        self.assertIn(response.status_code, [200, 302])

    def test_managermusiclabelerstream_requires_role(self):
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerMusicLabelerStream', kwargs={'music_id': 1}))
        self.assertIn(response.status_code, [302, 403, 404])
