"""
Test d'intégration pour la route: suppression d'un lien musical (/playlist/<uuid:playlist_uuid>/link/delete/<int:link_id>)
"""
from django.test import tag
from django.urls import reverse
import uuid

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.LinkMusic import LinkMusic
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase


@tag('integration')
class DeleteLinkRouteTest(AuthenticatedTestCase):
    """Tests pour la route link_delete (DELETE)"""

    def setUp(self):
        super().setUp()
        self.other_user = self.create_user(username='other')

        self.playlist = self.create_playlist(
            name='Ma playlist', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )
        self.other_playlist = self.create_playlist(
            user=self.other_user, name='Playlist autre', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )
        self.link = LinkMusic.objects.create(
            playlist=self.playlist, url='https://example.com/music.mp3', alternativeName='Lien'
        )

    def _url(self, playlist_uuid=None, link_id=None):
        return reverse('deleteLink', kwargs={
            'playlist_uuid': playlist_uuid or self.playlist.uuid,
            'link_id': link_id if link_id is not None else self.link.id,
        })

    def test_requires_authentication(self):
        response = self.client.delete(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_deletes_own_link(self):
        self.login()
        response = self.client.delete(self._url())
        self.assertEqual(response.status_code, 200)
        self.assertFalse(LinkMusic.objects.filter(pk=self.link.pk).exists())

    def test_returns_404_for_nonexistent_playlist(self):
        self.login()
        response = self.client.delete(self._url(playlist_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_other_users_playlist(self):
        self.login()
        response = self.client.delete(self._url(playlist_uuid=self.other_playlist.uuid))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_nonexistent_link(self):
        self.login()
        response = self.client.delete(self._url(link_id=999999))
        self.assertEqual(response.status_code, 404)

    def test_returns_405_on_get_request(self):
        self.login()
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 405)
