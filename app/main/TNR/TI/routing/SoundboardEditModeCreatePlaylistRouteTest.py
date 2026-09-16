"""
Test d'intégration pour la route: soundboardEditModeCreatePlaylist (POST /soundBoards/<uuid>/edit-mode/create)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.UserTier import UserTier
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
import uuid

User = get_user_model()


@tag('integration')
class SoundboardEditModeCreatePlaylistRouteTest(TestCase):
    """Tests pour la route soundboardEditModeCreatePlaylist (POST)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        self.soundboard = SoundBoard.objects.create(user=self.user, name='Board')

    def _url(self, soundboard_uuid=None):
        return reverse('soundboardEditModeCreatePlaylist', kwargs={
            'soundboard_uuid': soundboard_uuid or self.soundboard.uuid
        })

    def _valid_payload(self):
        return {
            'name': 'Ma nouvelle playlist',
            'typePlaylist': PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        }

    def test_requires_authentication(self):
        response = self.client.post(self._url(), self._valid_payload())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_creates_playlist_and_returns_201(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(), self._valid_payload())
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('playlist_uuid', data)

    def test_playlist_is_added_to_soundboard(self):
        self.client.login(username='owner', password='pw')
        self.client.post(self._url(), self._valid_payload())
        playlist = Playlist.objects.get(name='Ma nouvelle playlist')
        self.assertTrue(
            SoundboardPlaylist.objects.filter(SoundBoard=self.soundboard, Playlist=playlist).exists()
        )

    def test_returns_404_for_nonexistent_soundboard(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(soundboard_uuid=uuid.uuid4()), self._valid_payload())
        self.assertEqual(response.status_code, 404)

    def test_returns_400_when_name_missing(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(), {'typePlaylist': PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name})
        self.assertEqual(response.status_code, 400)

    def test_returns_400_when_type_invalid(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(), {'name': 'Playlist', 'typePlaylist': 'INVALID_TYPE'})
        self.assertEqual(response.status_code, 400)

    def test_returns_403_when_playlist_limit_reached(self):
        UserTier.objects.create(user=self.user, tier_name='STANDARD')
        limit = UserTier.objects.get(user=self.user)
        from main.domain.common.factory.UserParametersFactory import UserParametersFactory
        limit_playlist = UserParametersFactory(self.user).limit_playlist
        for i in range(limit_playlist):
            Playlist.objects.create(user=self.user, name=f'Playlist {i}')

        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(), self._valid_payload())
        self.assertEqual(response.status_code, 403)

    def test_returns_405_on_get_request(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 405)
