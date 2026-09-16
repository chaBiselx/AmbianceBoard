"""
Test d'intégration pour la route: création d'un lien musical via AJAX (/playlist/<uuid:playlist_uuid>/link/create-ajax)
"""
from django.test import tag
from django.urls import reverse
import uuid

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.LinkMusic import LinkMusic
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase


@tag('integration')
class AddLinkAjaxRouteTest(AuthenticatedTestCase):
    """Tests pour la route link_create_ajax (POST)"""

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
        return reverse('addLinkAjax', kwargs={'playlist_uuid': playlist_uuid or self.playlist.uuid})

    def test_requires_authentication(self):
        response = self.client.post(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_404_for_nonexistent_playlist(self):
        self.login()
        response = self.client.post(self._url(playlist_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_other_users_playlist(self):
        self.login()
        response = self.client.post(self._url(playlist_uuid=self.other_playlist.uuid))
        self.assertEqual(response.status_code, 404)

    def test_creates_link_and_returns_success_json(self):
        self.login()
        response = self.client.post(self._url(), {
            'url': 'https://example.com/music.mp3',
            'alternativeName': 'Mon lien',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(LinkMusic.objects.filter(playlist=self.playlist, alternativeName='Mon lien').exists())

    def test_returns_405_on_get_request(self):
        self.login()
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 405)
