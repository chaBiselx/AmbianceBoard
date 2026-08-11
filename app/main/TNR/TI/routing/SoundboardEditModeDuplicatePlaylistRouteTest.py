"""
Tests d'intégration pour la route:
soundboardEditModeDuplicatePlaylist (POST /soundBoards/<uuid>/edit-mode/duplicate/<uuid>)
"""
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, tag
from django.urls import reverse

from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.TrackLabel import TrackLabel
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class SoundboardEditModeDuplicatePlaylistRouteTest(TestCase):
    """Tests pour la route soundboardEditModeDuplicatePlaylist (POST)."""

    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username='board-owner',
            email='board-owner@test.com',
            password='testpassOwnser1234'
        )
        self.source_user = User.objects.create_user(
            username='source-owner',
            email='source-owner@test.com',
            password='testpassSource123'
        )

        self.soundboard = SoundBoard.objects.create(user=self.owner, name='Board édition')
        self.source_playlist = Playlist.objects.create(
            user=self.source_user,
            name='Playlist publique à copier',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
        )

        self.music = Music.objects.create(
            playlist=self.source_playlist,
            fileName='labeled-track.mp3',
            file=SimpleUploadedFile('labeled-track.mp3', b'fake audio content', content_type='audio/mpeg'),
            alternativeName='Track étiquetée',
            duration=12.5,
        )
        TrackLabel.objects.create(
            track=self.music,
            category='environment',
            label='void',
            confidence=0.91,
        )

    def _url(self, soundboard_uuid=None, playlist_uuid=None):
        return reverse('soundboardEditModeDuplicatePlaylist', kwargs={
            'soundboard_uuid': soundboard_uuid or self.soundboard.uuid,
            'playlist_uuid': playlist_uuid or self.source_playlist.uuid,
        })

    def test_duplicates_playlist_with_track_labels_and_adds_it_to_soundboard(self):
        self.client.login(username='board-owner', password='testpassOwnser1234')

        response = self.client.post(self._url())

        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertEqual(payload['message'], 'Playlist ajoutée en mode édition')
        self.assertIn('playlist_uuid', payload)
        self.assertIn('playlist_html', payload)
        self.assertIn('Playlist publique à copier (copie)', payload['playlist_html'])

        duplicated_playlist = Playlist.objects.get(uuid=payload['playlist_uuid'])
        self.assertEqual(duplicated_playlist.user, self.owner)
        self.assertTrue(
            SoundboardPlaylist.objects.filter(
                SoundBoard=self.soundboard,
                Playlist=duplicated_playlist,
            ).exists()
        )