"""
Test d'intégration pour la route: listSoundboardPlaylistsSpecific (GET /soundBoards/<uuid>/specific)
"""
from django.test import tag
from django.urls import reverse
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase
import uuid


@tag('integration')
class ListSoundboardPlaylistsSpecificRouteTest(AuthenticatedTestCase):
    """Tests pour la route listSoundboardPlaylistsSpecific (GET)."""

    def setUp(self):
        super().setUp()
        self.other_user = self.create_user(username='other')

        self.soundboard = self.create_soundboard(name='Board')
        self.playlist = self.create_playlist(
            name='Playlist',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )
        self.link_playlist(self.soundboard, self.playlist)

    def _url(self, soundboard_uuid=None):
        return reverse('listSoundboardPlaylistsSpecific', kwargs={
            'soundboard_uuid': soundboard_uuid or self.soundboard.uuid
        })

    def test_requires_authentication(self):
        response = self.client.get(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_200_for_owner(self):
        self.login()
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_returns_404_for_nonexistent_soundboard(self):
        self.login()
        response = self.client.get(self._url(soundboard_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_other_users_soundboard(self):
        self.login(self.other_user)
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 404)

    def test_contains_playlist_name(self):
        self.login()
        response = self.client.get(self._url())
        content = response.content.decode('utf-8')
        self.assertIn(self.playlist.name, content)
