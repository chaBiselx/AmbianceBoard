"""
Tests unitaires pour le service PlaylistProposalService.
"""

from unittest.mock import patch
from django.test import TestCase, tag
from main.domain.common.service.PlaylistProposalService import PlaylistProposalService
from main.domain.common.exceptions.PlaylistProposalException import (
    PlaylistProposalAlreadyExistsException,
    PlaylistProposalNotEligibleException,
    PlaylistProposalUnauthorizedException,
    PlaylistProposalInvalidStatusException,
)
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.PlaylistDuplicationHistory import PlaylistDuplicationHistory
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.enum.PlaylistProposalStatusEnum import PlaylistProposalStatusEnum


@tag('unitaire')
@patch('main.domain.common.service.PlaylistProposalService.UserMail')
class PlaylistProposalServiceTest(TestCase):

    def setUp(self):
        self.proposer = User.objects.create(username="proposer", email="proposer@test.com")
        self.owner = User.objects.create(username="owner", email="owner@test.com")

        self.soundboard = SoundBoard.objects.create(user=self.owner, name="Board public", is_public=True)
        self.playlist = Playlist.objects.create(
            user=self.proposer,
            name="Playlist proposable",
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
        )
        self.service = PlaylistProposalService()

    def test_propose_creates_pending_proposal(self, mock_user_mail):
        proposal = self.service.propose(self.playlist, self.soundboard, self.proposer)

        self.assertEqual(proposal.status, PlaylistProposalStatusEnum.PENDING.name)
        self.assertEqual(proposal.playlist, self.playlist)
        self.assertEqual(proposal.soundboard, self.soundboard)
        self.assertEqual(proposal.proposer, self.proposer)
        mock_user_mail.return_value.playlist_proposal_received.assert_called_once()

    def test_propose_raises_when_playlist_not_copiable(self, mock_user_mail):
        self.playlist.is_copiable = False
        self.playlist.save()

        with self.assertRaises(PlaylistProposalNotEligibleException):
            self.service.propose(self.playlist, self.soundboard, self.proposer)

    def test_propose_raises_when_not_owner_of_playlist(self, mock_user_mail):
        with self.assertRaises(PlaylistProposalUnauthorizedException):
            self.service.propose(self.playlist, self.soundboard, self.owner)

    def test_propose_raises_when_soundboard_not_public(self, mock_user_mail):
        self.soundboard.is_public = False
        self.soundboard.save()

        with self.assertRaises(PlaylistProposalUnauthorizedException):
            self.service.propose(self.playlist, self.soundboard, self.proposer)

    def test_propose_raises_when_already_proposed(self, mock_user_mail):
        self.service.propose(self.playlist, self.soundboard, self.proposer)

        with self.assertRaises(PlaylistProposalAlreadyExistsException):
            self.service.propose(self.playlist, self.soundboard, self.proposer)

    def test_withdraw_deletes_pending_proposal(self, mock_user_mail):
        proposal = self.service.propose(self.playlist, self.soundboard, self.proposer)

        self.service.withdraw(proposal, self.proposer)

        self.assertEqual(self.playlist.proposals.count(), 0)

    def test_withdraw_raises_for_other_user(self, mock_user_mail):
        proposal = self.service.propose(self.playlist, self.soundboard, self.proposer)

        with self.assertRaises(PlaylistProposalUnauthorizedException):
            self.service.withdraw(proposal, self.owner)

    def test_accept_duplicates_playlist_and_adds_to_soundboard(self, mock_user_mail):
        proposal = self.service.propose(self.playlist, self.soundboard, self.proposer)

        duplicated_playlist = self.service.accept(proposal, self.owner)

        proposal.refresh_from_db()
        self.assertEqual(proposal.status, PlaylistProposalStatusEnum.ACCEPTED.name)
        self.assertEqual(proposal.duplicated_playlist, duplicated_playlist)
        self.assertEqual(duplicated_playlist.user, self.owner)
        self.assertTrue(
            SoundboardPlaylist.objects.filter(SoundBoard=self.soundboard, Playlist=duplicated_playlist).exists()
        )

    def test_accept_reuses_existing_duplication(self, mock_user_mail):
        proposal = self.service.propose(self.playlist, self.soundboard, self.proposer)

        existing_duplicated_playlist = Playlist.objects.create(
            user=self.owner,
            name="Déjà dupliquée",
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )
        PlaylistDuplicationHistory.objects.create(
            source_playlist=self.playlist,
            duplicated_playlist=existing_duplicated_playlist,
            source_playlist_name=self.playlist.name,
            source_playlist_uuid=self.playlist.uuid,
        )

        duplicated_playlist = self.service.accept(proposal, self.owner)

        self.assertEqual(duplicated_playlist, existing_duplicated_playlist)

    def test_accept_raises_when_not_soundboard_owner(self, mock_user_mail):
        proposal = self.service.propose(self.playlist, self.soundboard, self.proposer)

        with self.assertRaises(PlaylistProposalUnauthorizedException):
            self.service.accept(proposal, self.proposer)

    def test_accept_raises_when_not_pending(self, mock_user_mail):
        proposal = self.service.propose(self.playlist, self.soundboard, self.proposer)
        self.service.refuse(proposal, self.owner)

        with self.assertRaises(PlaylistProposalInvalidStatusException):
            self.service.accept(proposal, self.owner)

    def test_refuse_marks_proposal_as_refused(self, mock_user_mail):
        proposal = self.service.propose(self.playlist, self.soundboard, self.proposer)

        self.service.refuse(proposal, self.owner)

        proposal.refresh_from_db()
        self.assertEqual(proposal.status, PlaylistProposalStatusEnum.REFUSED.name)
        self.assertEqual(proposal.resolved_by, self.owner)

    def test_dismiss_deletes_refused_proposal(self, mock_user_mail):
        proposal = self.service.propose(self.playlist, self.soundboard, self.proposer)
        self.service.refuse(proposal, self.owner)

        self.service.dismiss(proposal, self.proposer)

        self.assertEqual(self.playlist.proposals.count(), 0)
