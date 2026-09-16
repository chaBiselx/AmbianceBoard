"""
Test d'intégration pour la route: stream d'une track de proposition
(/soundBoards/propositions/<uuid:proposal_uuid>/track/<int:music_id>/stream)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import uuid

from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.PlaylistProposal import PlaylistProposal
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class PlaylistProposalTrackStreamRouteTest(TestCase):
    """Tests pour la route playlist_proposal_track_stream (GET/HEAD)"""

    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        self.soundboard = SoundBoard.objects.create(user=self.owner, name='Board')
        self.playlist = Playlist.objects.create(
            user=self.other_user, name='Playlist proposée', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )
        self.music = Music.objects.create(
            playlist=self.playlist,
            fileName='track.mp3',
            file=SimpleUploadedFile('track.mp3', b'fake audio content', content_type='audio/mpeg'),
            alternativeName='Track',
            duration=10.0,
        )
        self.proposal = PlaylistProposal.objects.create(
            playlist=self.playlist, soundboard=self.soundboard, proposer=self.other_user
        )

    def _url(self, proposal_uuid=None, music_id=None):
        return reverse('playlistProposalTrackStream', kwargs={
            'proposal_uuid': proposal_uuid or self.proposal.uuid,
            'music_id': music_id if music_id is not None else self.music.id,
        })

    def test_requires_authentication(self):
        response = self.client.get(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_200_for_soundboard_owner(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_head_returns_content_duration_header(self):
        self.client.login(username='owner', password='pw')
        response = self.client.head(self._url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Duration'], '10.0')

    def test_returns_404_for_non_owner_of_soundboard(self):
        self.client.login(username='other', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_nonexistent_proposal(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url(proposal_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_nonexistent_music(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url(music_id=999999))
        self.assertEqual(response.status_code, 404)
