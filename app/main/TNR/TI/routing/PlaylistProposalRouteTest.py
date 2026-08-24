"""
Tests d'intégration pour les routes de proposition de playlist:
- POST /public/soundboards/<uuid>/propose/<uuid> (publicSoundboardProposePlaylist)
- POST /public/soundboards/<uuid>/propose/<uuid>/withdraw (publicSoundboardWithdrawProposal)
- POST /soundBoards/propositions/<uuid>/accept (playlistProposalAccept)
- POST /soundBoards/propositions/<uuid>/refuse (playlistProposalRefuse)
"""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, tag
from django.urls import reverse

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.PlaylistProposal import PlaylistProposal
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.enum.PlaylistProposalStatusEnum import PlaylistProposalStatusEnum

User = get_user_model()


@tag('integration')
class PlaylistProposalRouteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username='board-owner', email='board-owner@test.com', password='testpassOwner1234'
        )
        self.proposer = User.objects.create_user(
            username='proposer-user', email='proposer-user@test.com', password='testpassProposer1234'
        )

        self.soundboard = SoundBoard.objects.create(user=self.owner, name='Board public', is_public=True)
        self.playlist = Playlist.objects.create(
            user=self.proposer,
            name='Playlist à proposer',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
        )

    def test_propose_playlist_creates_pending_proposal(self):
        self.client.login(username='proposer-user', password='testpassProposer1234')

        response = self.client.post(
            reverse('publicSoundboardProposePlaylist', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'playlist_uuid': self.playlist.uuid,
            })
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(PlaylistProposal.objects.count(), 1)
        proposal = PlaylistProposal.objects.first()
        self.assertEqual(proposal.status, PlaylistProposalStatusEnum.PENDING.name)

    def test_propose_playlist_requires_authentication(self):
        response = self.client.post(
            reverse('publicSoundboardProposePlaylist', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'playlist_uuid': self.playlist.uuid,
            })
        )
        self.assertEqual(response.status_code, 302)

    def test_withdraw_proposal(self):
        self.client.login(username='proposer-user', password='testpassProposer1234')
        proposal = PlaylistProposal.objects.create(
            playlist=self.playlist, soundboard=self.soundboard, proposer=self.proposer
        )

        response = self.client.post(
            reverse('publicSoundboardWithdrawProposal', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'proposal_uuid': proposal.uuid,
            })
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(PlaylistProposal.objects.count(), 0)

    def test_accept_proposal_adds_duplicated_playlist_to_soundboard(self):
        self.client.login(username='board-owner', password='testpassOwner1234')
        proposal = PlaylistProposal.objects.create(
            playlist=self.playlist, soundboard=self.soundboard, proposer=self.proposer
        )

        response = self.client.post(
            reverse('playlistProposalAccept', kwargs={'proposal_uuid': proposal.uuid})
        )

        self.assertEqual(response.status_code, 200)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, PlaylistProposalStatusEnum.ACCEPTED.name)
        self.assertTrue(
            SoundboardPlaylist.objects.filter(SoundBoard=self.soundboard, Playlist=proposal.duplicated_playlist).exists()
        )

    def test_accept_proposal_forbidden_for_non_owner(self):
        self.client.login(username='proposer-user', password='testpassProposer1234')
        proposal = PlaylistProposal.objects.create(
            playlist=self.playlist, soundboard=self.soundboard, proposer=self.proposer
        )

        response = self.client.post(
            reverse('playlistProposalAccept', kwargs={'proposal_uuid': proposal.uuid})
        )

        self.assertEqual(response.status_code, 403)

    def test_refuse_proposal(self):
        self.client.login(username='board-owner', password='testpassOwner1234')
        proposal = PlaylistProposal.objects.create(
            playlist=self.playlist, soundboard=self.soundboard, proposer=self.proposer
        )

        response = self.client.post(
            reverse('playlistProposalRefuse', kwargs={'proposal_uuid': proposal.uuid})
        )

        self.assertEqual(response.status_code, 200)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, PlaylistProposalStatusEnum.REFUSED.name)
