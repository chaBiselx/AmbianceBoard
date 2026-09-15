"""
Test d'intégration pour la route: suppression d'une playlist (/playlist/<uuid:playlist_uuid>/delete)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

from main.architecture.persistence.models.Playlist import Playlist
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class PlaylistDeleteRouteTest(TestCase):
    """Tests pour la route playlist_delete (DELETE)"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        self.playlist = Playlist.objects.create(
            user=self.user, name='Ma playlist', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )
        self.other_playlist = Playlist.objects.create(
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
