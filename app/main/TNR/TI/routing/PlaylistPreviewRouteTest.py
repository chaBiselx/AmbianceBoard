"""
Test d'intégration pour la route: prévisualisation d'une playlist copiable (/playlist/public/copiable)
"""
from django.test import tag
from django.urls import reverse
import uuid

from main.architecture.persistence.models.Playlist import Playlist
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase


@tag('integration')
class PlaylistPreviewRouteTest(AuthenticatedTestCase):
    """Tests pour la route playlist_copiable_preview (GET)"""

    def setUp(self):
        super().setUp()
        self.other_user = self.create_user(username='other')

        self.copiable_playlist = self.create_playlist(
            user=self.other_user, name='Playlist copiable', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
        )
        self.non_copiable_playlist = self.create_playlist(
            user=self.other_user, name='Playlist non copiable', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=False,
        )
        self.banned_playlist = self.create_playlist(
            user=self.other_user, name='Playlist bannie', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True, moderator_ban_copie=True,
        )

    def _url(self, playlist_uuid=None):
        url = reverse('playlistPreview')
        if playlist_uuid is not None:
            url += f'?playlistUuid={playlist_uuid}'
        return url

    def test_requires_authentication(self):
        response = self.client.get(self._url(self.copiable_playlist.uuid))
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_404_when_missing_query_param(self):
        self.login()
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_nonexistent_playlist(self):
        self.login()
        response = self.client.get(self._url(uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_non_copiable_playlist(self):
        self.login()
        response = self.client.get(self._url(self.non_copiable_playlist.uuid))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_banned_playlist(self):
        self.login()
        response = self.client.get(self._url(self.banned_playlist.uuid))
        self.assertEqual(response.status_code, 404)

    def test_returns_200_for_copiable_playlist(self):
        self.login()
        response = self.client.get(self._url(self.copiable_playlist.uuid))
        self.assertEqual(response.status_code, 200)
