"""Test d'intégration pour la suppression d'une playlist."""
from django.test import tag
from django.urls import reverse
import uuid

from main.architecture.persistence.models.Playlist import Playlist
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase


@tag('integration')
class PlaylistDeleteRouteTest(AuthenticatedTestCase):
    """Tests pour la route playlist_delete (DELETE)"""

    def setUp(self):
        super().setUp()
        self.other_user = self.create_user(username='other')

        self.playlist = self.create_playlist(
            name='Ma playlist', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )
        self.other_playlist = self.create_playlist(
            user=self.other_user, name='Playlist autre', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )

    def _url(self, playlist_uuid=None):
        return reverse('playlistDelete', kwargs={'playlist_uuid': playlist_uuid or self.playlist.uuid})

    def test_requires_authentication(self):
        response = self.client.delete(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_deletes_own_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.delete(self._url())
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Playlist.objects.filter(pk=self.playlist.pk).exists())

    def test_returns_404_for_nonexistent_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.delete(self._url(playlist_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_other_users_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.delete(self._url(playlist_uuid=self.other_playlist.uuid))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Playlist.objects.filter(pk=self.other_playlist.pk).exists())

    def test_returns_405_on_get_request(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 405)
