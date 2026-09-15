"""
Test d'intégration pour la route: Streaming d'une musique de proposition en session partagée
(/shared/<uuid:soundboard_uuid>/<str:token>/proposal/<uuid:proposal_uuid>/<int:music_id>/stream)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SharedSoundboard import SharedSoundboard
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.PlaylistProposal import PlaylistProposal
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class SharedProposalStreamMusicRouteTest(TestCase):
    """Tests pour la route de streaming d'une musique de proposition partagée"""

    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='shared_proposal_owner', email='shared_proposal_owner@test.com', password='Test1234!')
        self.proposer = User.objects.create_user(username='shared_proposal_proposer', email='shared_proposal_proposer@test.com', password='Test1234!')
        self.soundboard = SoundBoard.objects.create(user=self.owner, name='SB Shared Proposal')
        self.shared = SharedSoundboard.objects.create(soundboard=self.soundboard)
        self.playlist = Playlist.objects.create(
            user=self.proposer,
            name='Playlist Shared Proposal',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
        )
        self.proposal = PlaylistProposal.objects.create(
            playlist=self.playlist, soundboard=self.soundboard, proposer=self.proposer
        )

    def test_shared_proposal_stream_with_invalid_token(self):
        """Test avec un token invalide"""
        response = self.client.get(
            reverse('sharedProposalStreamMusic', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'token': 'invalid-token',
                'proposal_uuid': self.proposal.uuid,
                'music_id': 1,
            })
        )
        self.assertEqual(response.status_code, 404)

    def test_shared_proposal_stream_with_invalid_uuid(self):
        """Test avec un UUID de soundboard inexistant"""
        response = self.client.get(
            reverse('sharedProposalStreamMusic', kwargs={
                'soundboard_uuid': uuid.uuid4(),
                'token': str(self.shared.token),
                'proposal_uuid': self.proposal.uuid,
                'music_id': 1,
            })
        )
        self.assertEqual(response.status_code, 404)

    def test_shared_proposal_stream_with_invalid_proposal_uuid(self):
        """Test avec une proposition inexistante mais un token de session valide"""
        response = self.client.get(
            reverse('sharedProposalStreamMusic', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'token': str(self.shared.token),
                'proposal_uuid': uuid.uuid4(),
                'music_id': 1,
            })
        )
        self.assertEqual(response.status_code, 404)

    def test_shared_proposal_stream_accessible_without_auth(self):
        """Test que la route est accessible sans authentification (session partagée par token)"""
        response = self.client.get(
            reverse('sharedProposalStreamMusic', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'token': str(self.shared.token),
                'proposal_uuid': self.proposal.uuid,
                'music_id': 99999,
            })
        )
        self.assertEqual(response.status_code, 404)
