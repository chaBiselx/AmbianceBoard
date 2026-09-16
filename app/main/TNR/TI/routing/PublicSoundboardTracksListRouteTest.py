"""
Test d'intégration pour la route: Liste des tracks d'un soundboard public
(/public/soundboards/<uuid:soundboard_uuid>/fetch/tracks)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid
import json

from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.Track import Track
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class PublicSoundboardTracksListRouteTest(TestCase):
    """Tests pour la route de liste des tracks d'un soundboard public"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tracks_list_owner', email='tracks_list_owner@test.com', password='Test1234!')
        self.playlist = Playlist.objects.create(
            user=self.user,
            name='Playlist Tracks List',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )
        self.track = Track.objects.create(playlist=self.playlist, alternativeName='Track One')

    def _create_public_soundboard(self, is_public=True):
        soundboard = SoundBoard.objects.create(user=self.user, name='SB Tracks', is_public=is_public)
        soundboard.playlists.add(self.playlist)
        return soundboard

    def test_tracks_list_accessible_without_auth(self):
        """Test que la route est accessible sans authentification"""
        soundboard = self._create_public_soundboard()
        response = self.client.get(
            reverse('publicSoundboardTracksList', kwargs={'soundboard_uuid': soundboard.uuid})
        )
        self.assertEqual(response.status_code, 200)

    def test_tracks_list_returns_expected_json_shape(self):
        """La réponse JSON contient les playlists avec leurs tracks"""
        soundboard = self._create_public_soundboard()
        response = self.client.get(
            reverse('publicSoundboardTracksList', kwargs={'soundboard_uuid': soundboard.uuid})
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn(str(self.playlist.uuid), data)
        tracks = data[str(self.playlist.uuid)]
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]['id'], self.track.id)
        self.assertEqual(tracks[0]['name'], 'Track One')
        self.assertIn('uri', tracks[0])

    def test_tracks_list_with_invalid_uuid(self):
        """Test avec un UUID inexistant"""
        response = self.client.get(
            reverse('publicSoundboardTracksList', kwargs={'soundboard_uuid': uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 404)

    def test_tracks_list_with_private_soundboard(self):
        """Un soundboard non public ne doit pas être accessible"""
        soundboard = self._create_public_soundboard(is_public=False)
        response = self.client.get(
            reverse('publicSoundboardTracksList', kwargs={'soundboard_uuid': soundboard.uuid})
        )
        self.assertEqual(response.status_code, 404)
