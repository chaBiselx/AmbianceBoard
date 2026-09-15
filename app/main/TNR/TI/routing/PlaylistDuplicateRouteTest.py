"""
Test d'intégration pour la route: duplication d'une playlist copiable
(/playlist/public/copiable/<uuid:playlist_uuid>/duplicate)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

from main.architecture.persistence.models.Playlist import Playlist
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class PlaylistDuplicateRouteTest(TestCase):
    """Tests pour la route playlist_copiable_duplicate (POST)"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        self.copiable_playlist = Playlist.objects.create(
            user=self.other_user, name='Playlist copiable', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
        )
        self.non_copiable_playlist = Playlist.objects.create(
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
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('new_playlist_uuid', data)
        self.assertTrue(Playlist.objects.filter(uuid=data['new_playlist_uuid'], user=self.user).exists())

    def test_returns_404_for_nonexistent_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(playlist_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_403_for_non_copiable_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(playlist_uuid=self.non_copiable_playlist.uuid))
        self.assertEqual(response.status_code, 403)

    def test_returns_409_when_already_duplicated(self):
        self.client.login(username='owner', password='pw')
        self.client.post(self._url())
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 409)

    def test_returns_405_on_get_request(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 405)
