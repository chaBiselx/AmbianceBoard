"""
Test d'intégration pour la route: upload multiple de musiques (/playlist/<uuid:playlist_uuid>/music/upload-multiple)
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
class UploadMultipleMusicRouteTest(TestCase):
    """Tests pour la route upload_multiple_music (POST)"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR

        self.playlist = Playlist.objects.create(
            user=self.user, name='Ma playlist', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )

    def _url(self, playlist_uuid=None):
        return reverse('uploadMultipleMusic', kwargs={'playlist_uuid': playlist_uuid or self.playlist.uuid})

    def test_requires_authentication(self):
        response = self.client.post(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_404_for_nonexistent_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(playlist_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_400_when_no_files_sent(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 400)

    def test_uploads_multiple_valid_files(self):
        self.client.login(username='owner', password='pw')
        file1 = SimpleUploadedFile('song1.mp3', b'fake audio content 1', content_type='audio/mpeg')
        file2 = SimpleUploadedFile('song2.mp3', b'fake audio content 2', content_type='audio/mpeg')
        response = self.client.post(self._url(), {'file1': file1, 'file2': file2})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['uploaded_files']), 2)
        self.assertEqual(Music.objects.filter(playlist=self.playlist).count(), 2)

    def test_returns_400_for_invalid_file_extension(self):
        self.client.login(username='owner', password='pw')
        bad_file = SimpleUploadedFile('document.txt', b'not audio', content_type='text/plain')
        response = self.client.post(self._url(), {'file1': bad_file})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])

    def test_returns_405_on_get_request(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 405)
