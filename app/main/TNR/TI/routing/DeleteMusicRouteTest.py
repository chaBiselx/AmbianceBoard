"""
Test d'intégration pour la route: suppression d'une musique (/playlist/<uuid:playlist_uuid>/music/delete/<int:music_id>)
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
class DeleteMusicRouteTest(TestCase):
    """Tests pour la route music_delete (DELETE)"""

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
        self.music = Music.objects.create(
            playlist=self.playlist,
            fileName='track.mp3',
            file=SimpleUploadedFile('track.mp3', b'fake audio content', content_type='audio/mpeg'),
            alternativeName='Track',
        )

    def _url(self, playlist_uuid=None, music_id=None):
        return reverse('deleteMusic', kwargs={
            'playlist_uuid': playlist_uuid or self.playlist.uuid,
            'music_id': music_id if music_id is not None else self.music.id,
        })

    def test_requires_authentication(self):
        response = self.client.delete(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_deletes_own_music(self):
        self.client.login(username='owner', password='pw')
        response = self.client.delete(self._url())
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Music.objects.filter(pk=self.music.pk).exists())

    def test_returns_404_for_nonexistent_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.delete(self._url(playlist_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_other_users_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.delete(self._url(playlist_uuid=self.other_playlist.uuid))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_nonexistent_music(self):
        self.client.login(username='owner', password='pw')
        response = self.client.delete(self._url(music_id=999999))
        self.assertEqual(response.status_code, 404)

    def test_returns_405_on_get_request(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 405)
