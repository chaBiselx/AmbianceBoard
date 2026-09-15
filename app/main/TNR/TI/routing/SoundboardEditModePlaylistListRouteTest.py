"""
Test d'intégration pour la route: soundboardEditModePlaylistList (GET /soundBoards/<uuid>/edit-mode/playlist-list)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.Track import Track
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
import uuid

User = get_user_model()


@tag('integration')
class SoundboardEditModePlaylistListRouteTest(TestCase):
    """Tests pour la route soundboardEditModePlaylistList (GET)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        self.soundboard = SoundBoard.objects.create(user=self.user, name='Board')

        self.copiable_playlist = Playlist.objects.create(
            user=self.other_user, name='Copiable', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True, moderator_ban_copie=False
        )
        Track.objects.create(playlist=self.copiable_playlist, alternativeName='Track')

        self.not_copiable_playlist = Playlist.objects.create(
            user=self.other_user, name='Non copiable', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=False
        )
        Track.objects.create(playlist=self.not_copiable_playlist, alternativeName='Track')

    def _url(self, soundboard_uuid=None):
        return reverse('soundboardEditModePlaylistList', kwargs={
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

    def test_response_contains_copiable_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        content = response.content.decode('utf-8')
        self.assertIn(self.copiable_playlist.name, content)

    def test_response_excludes_non_copiable_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        content = response.content.decode('utf-8')
        self.assertNotIn(self.not_copiable_playlist.name, content)

    def test_type_filter_is_applied(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url(), {'playlistType': PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.value})
        content = response.content.decode('utf-8')
        self.assertNotIn(self.copiable_playlist.name, content)

    def test_page_query_param_is_accepted(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url(), {'page': 1})
        self.assertEqual(response.status_code, 200)
