"""
Test d'intégration pour la route: mise à jour d'une musique (/playlist/<uuid:playlist_uuid>/music/edit/<int:music_id>)
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
class EditMusicRouteTest(AuthenticatedTestCase):
    """Tests pour la route music_update (GET/POST)"""

    def setUp(self):
        super().setUp()
        self.other_user = self.create_user(username='other')

        self.playlist = self.create_playlist(
            name='Ma playlist', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )
        self.other_playlist = self.create_playlist(
            user=self.other_user, name='Playlist autre', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )
        self.music = Music.objects.create(
            playlist=self.playlist,
            fileName='track.mp3',
            file=SimpleUploadedFile('track.mp3', b'fake audio content', content_type='audio/mpeg'),
            alternativeName='Track originale',
        )

    def _url(self, playlist_uuid=None, music_id=None):
        return reverse('editMusic', kwargs={
            'playlist_uuid': playlist_uuid or self.playlist.uuid,
            'music_id': music_id if music_id is not None else self.music.id,
        })

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

    def test_returns_404_for_nonexistent_music(self):
        self.login()
        response = self.client.get(self._url(music_id=999999))
        self.assertEqual(response.status_code, 404)

    def test_post_updates_music_and_redirects(self):
        self.login()
        response = self.client.post(self._url(), {
            'alternativeName': 'Track renommée',
        })
        self.assertEqual(response.status_code, 302)
        self.music.refresh_from_db()
        self.assertEqual(self.music.alternativeName, 'Track renommée')
