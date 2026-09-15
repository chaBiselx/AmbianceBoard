"""
Test d'intégration pour la route: Streaming public d'une track spécifique
(/public/soundboards/<uuid:soundboard_uuid>/<uuid:playlist_uuid>/<int:music_id>/stream)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.Track import Track
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class PublicSpecificTrackStreamRouteTest(TestCase):
    """Tests pour la route de streaming public d'une track spécifique"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='track_stream_owner', email='track_stream_owner@test.com', password='Test1234!')
        self.playlist = Playlist.objects.create(
            user=self.user,
            name='Playlist Track Stream',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )
        self.soundboard = SoundBoard.objects.create(user=self.user, name='SB Stream', is_public=True)
        self.soundboard.playlists.add(self.playlist)
        self.track = Track.objects.create(playlist=self.playlist, alternativeName='Track Stream')

    def test_specific_track_stream_accessible_without_auth(self):
        """Test que la route est accessible sans authentification"""
        response = self.client.get(
            reverse('publicSpecificTrackStream', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'playlist_uuid': self.playlist.uuid,
                'music_id': self.track.id,
            })
        )
        self.assertIn(response.status_code, [200, 404])

    def test_specific_track_stream_with_invalid_uuids(self):
        """Test avec des UUIDs invalides"""
        response = self.client.get(
            reverse('publicSpecificTrackStream', kwargs={
                'soundboard_uuid': uuid.uuid4(),
                'playlist_uuid': uuid.uuid4(),
                'music_id': 99999,
            })
        )
        self.assertEqual(response.status_code, 404)

    def test_specific_track_stream_metadata_only_without_cache_returns_404(self):
        """Sans cache préalable, une requête X-Metadata-Only doit échouer"""
        response = self.client.get(
            reverse('publicSpecificTrackStream', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'playlist_uuid': self.playlist.uuid,
                'music_id': self.track.id,
            }),
            HTTP_X_METADATA_ONLY='true',
        )
        self.assertEqual(response.status_code, 404)

    def test_specific_track_stream_with_private_soundboard(self):
        """Un soundboard non public ne doit pas être accessible via cette route"""
        self.soundboard.is_public = False
        self.soundboard.save()
        response = self.client.get(
            reverse('publicSpecificTrackStream', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'playlist_uuid': self.playlist.uuid,
                'music_id': self.track.id,
            })
        )
        self.assertEqual(response.status_code, 404)
