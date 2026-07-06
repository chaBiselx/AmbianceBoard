"""
Tests d'intégration pour les routes :
  - soundboardEditModeMyPlaylistList  (GET  /soundBoards/<uuid>/edit-mode/my-playlist-list)
  - soundboardEditModeAddMyPlaylist   (POST /soundBoards/<uuid>/edit-mode/add-my-playlist/<uuid>)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
import uuid

User = get_user_model()


@tag('integration')
class SoundboardEditModeMyPlaylistListRouteTest(TestCase):
    """Tests pour la route soundboardEditModeMyPlaylistList (GET)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        self.soundboard = SoundBoard.objects.create(user=self.user, name='Board')

        self.playlist_integrated = Playlist.objects.create(
            user=self.user, name='Intégrée', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )
        self.playlist_not_integrated = Playlist.objects.create(
            user=self.user, name='Non intégrée', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name
        )
        SoundboardPlaylist.objects.create(SoundBoard=self.soundboard, Playlist=self.playlist_integrated, order=1)

    def _url(self, soundboard_uuid=None):
        return reverse('soundboardEditModeMyPlaylistList', kwargs={
            'soundboard_uuid': soundboard_uuid or self.soundboard.uuid
        })

    def test_requires_authentication(self):
        response = self.client.get(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_200_for_owner(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_returns_404_for_nonexistent_soundboard(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url(soundboard_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_other_users_soundboard(self):
        self.client.login(username='other', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 404)

    def test_response_excludes_integrated_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        content = response.content.decode('utf-8')
        self.assertNotIn(self.playlist_integrated.name, content)

    def test_response_contains_non_integrated_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        content = response.content.decode('utf-8')
        self.assertIn(self.playlist_not_integrated.name, content)

    def test_type_filter_is_applied(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url(), {'playlistType': PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.value})
        content = response.content.decode('utf-8')
        self.assertNotIn(self.playlist_not_integrated.name, content)


@tag('integration')
class SoundboardEditModeAddMyPlaylistRouteTest(TestCase):
    """Tests pour la route soundboardEditModeAddMyPlaylist (POST)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        self.soundboard = SoundBoard.objects.create(user=self.user, name='Board')
        self.playlist = Playlist.objects.create(
            user=self.user, name='Ma playlist', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )
        self.other_playlist = Playlist.objects.create(
            user=self.other_user, name='Playlist autre', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )

    def _url(self, soundboard_uuid=None, playlist_uuid=None):
        return reverse('soundboardEditModeAddMyPlaylist', kwargs={
            'soundboard_uuid': soundboard_uuid or self.soundboard.uuid,
            'playlist_uuid': playlist_uuid or self.playlist.uuid,
        })

    def test_requires_authentication(self):
        response = self.client.post(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_add_playlist_returns_200_and_success(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('playlist_html', data)

    def test_playlist_is_added_to_soundboard(self):
        self.client.login(username='owner', password='pw')
        self.client.post(self._url())
        self.assertTrue(
            SoundboardPlaylist.objects.filter(SoundBoard=self.soundboard, Playlist=self.playlist).exists()
        )

    def test_returns_404_for_nonexistent_soundboard(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(soundboard_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_nonexistent_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(playlist_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_403_when_playlist_belongs_to_another_user(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(playlist_uuid=self.other_playlist.uuid))
        self.assertEqual(response.status_code, 403)

    def test_returns_409_when_playlist_already_in_soundboard(self):
        SoundboardPlaylist.objects.create(SoundBoard=self.soundboard, Playlist=self.playlist, order=1)
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 409)

    def test_returns_405_on_get_request(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 405)
