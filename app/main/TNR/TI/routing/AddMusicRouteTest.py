"""
Test d'intégration pour la route: création d'une musique (/playlist/<uuid:playlist_uuid>/music/create)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import uuid

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.Music import Music
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class AddMusicRouteTest(TestCase):
    """Tests pour la route music_create (GET/POST)"""

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
        return reverse('addMusic', kwargs={'playlist_uuid': playlist_uuid or self.playlist.uuid})

    def test_requires_authentication(self):
        response = self.client.get(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_200_for_owner(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_returns_404_for_nonexistent_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url(playlist_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_other_users_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url(playlist_uuid=self.other_playlist.uuid))
        self.assertEqual(response.status_code, 404)

    def test_post_creates_music_and_redirects(self):
        self.client.login(username='owner', password='pw')
        audio_file = SimpleUploadedFile('song.mp3', b'fake audio content', content_type='audio/mpeg')
        response = self.client.post(self._url(), {
            'file': audio_file,
            'alternativeName': 'Ma musique',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Music.objects.filter(playlist=self.playlist, alternativeName='Ma musique').exists())
