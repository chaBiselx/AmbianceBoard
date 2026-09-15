"""
Test d'intégration pour la route: création d'une musique (/playlist/<uuid:playlist_uuid>/music/create)
"""
from django.test import tag
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import uuid

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.Music import Music
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase


@tag('integration')
class AddMusicRouteTest(AuthenticatedTestCase):
    """Tests pour la route music_create (GET/POST)"""

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
        return reverse('addMusic', kwargs={'playlist_uuid': playlist_uuid or self.playlist.uuid})

    def test_requires_authentication(self):
        response = self.client.get(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_200_for_owner(self):
        self.login()
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_returns_404_for_nonexistent_playlist(self):
        self.login()
        response = self.client.get(self._url(playlist_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_other_users_playlist(self):
        self.login()
        response = self.client.get(self._url(playlist_uuid=self.other_playlist.uuid))
        self.assertEqual(response.status_code, 404)

    def test_post_creates_music_and_redirects(self):
        self.login()
        audio_file = SimpleUploadedFile('song.mp3', b'fake audio content', content_type='audio/mpeg')
        response = self.client.post(self._url(), {
            'file': audio_file,
            'alternativeName': 'Ma musique',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Music.objects.filter(playlist=self.playlist, alternativeName='Ma musique').exists())
