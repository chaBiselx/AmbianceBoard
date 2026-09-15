"""
Test d'intégration pour la route: duplication d'une playlist copiable
(/playlist/public/copiable/<uuid:playlist_uuid>/duplicate)
"""
from django.test import tag
from django.urls import reverse
import uuid

from main.architecture.persistence.models.Playlist import Playlist
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase


@tag('integration')
class PlaylistDuplicateRouteTest(AuthenticatedTestCase):
    """Tests pour la route playlist_copiable_duplicate (POST)"""

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

    def _url(self, playlist_uuid=None):
        return reverse('playlistDuplicate', kwargs={
            'playlist_uuid': playlist_uuid or self.copiable_playlist.uuid
        })

    def test_requires_authentication(self):
        response = self.client.post(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_duplicates_copiable_playlist(self):
        self.login()
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('new_playlist_uuid', data)
        self.assertTrue(Playlist.objects.filter(uuid=data['new_playlist_uuid'], user=self.user).exists())

    def test_returns_404_for_nonexistent_playlist(self):
        self.login()
        response = self.client.post(self._url(playlist_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_403_for_non_copiable_playlist(self):
        self.login()
        response = self.client.post(self._url(playlist_uuid=self.non_copiable_playlist.uuid))
        self.assertEqual(response.status_code, 403)

    def test_returns_409_when_already_duplicated(self):
        self.login()
        self.client.post(self._url())
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 409)

    def test_returns_405_on_get_request(self):
        self.login()
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 405)
