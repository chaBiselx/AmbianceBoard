from typing import Optional
from django.db.models import QuerySet
from main.architecture.persistence.models.PlaylistProposal import PlaylistProposal
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.User import User
from main.domain.common.enum.PlaylistProposalStatusEnum import PlaylistProposalStatusEnum


class PlaylistProposalRepository:
    """
    Repository pour gérer les opérations de base de données liées aux
    propositions de playlist sur les soundboards publics.
    """

    def create(self, playlist: Playlist, soundboard: SoundBoard, proposer: User) -> PlaylistProposal:
        proposal = PlaylistProposal(playlist=playlist, soundboard=soundboard, proposer=proposer)
        proposal.save()
        return proposal

    def get(self, proposal_uuid) -> Optional[PlaylistProposal]:
        try:
            return PlaylistProposal.objects.select_related(
                'playlist', 'soundboard', 'proposer', 'soundboard__user'
            ).get(uuid=proposal_uuid)
        except PlaylistProposal.DoesNotExist:
            return None

    def find_existing(self, playlist: Playlist, soundboard: SoundBoard) -> Optional[PlaylistProposal]:
        return PlaylistProposal.objects.filter(playlist=playlist, soundboard=soundboard).first()

    def get_pending_for_soundboard(self, soundboard: SoundBoard) -> QuerySet[PlaylistProposal]:
        return PlaylistProposal.objects.filter(
            soundboard=soundboard,
            status=PlaylistProposalStatusEnum.PENDING.name
        ).select_related('playlist', 'proposer').order_by('-created_at')

    def get_pending_for_owner(self, user: User) -> QuerySet[PlaylistProposal]:
        return PlaylistProposal.objects.filter(
            soundboard__user=user,
            status=PlaylistProposalStatusEnum.PENDING.name
        ).select_related('playlist', 'proposer', 'soundboard').order_by('-created_at')

    def count_pending_for_owner(self, user: User) -> int:
        return self.get_pending_for_owner(user).count()

    def get_for_proposer_and_soundboard(self, user: User, soundboard: SoundBoard) -> QuerySet[PlaylistProposal]:
        return PlaylistProposal.objects.filter(
            proposer=user,
            soundboard=soundboard,
            status__in=[PlaylistProposalStatusEnum.PENDING.name, PlaylistProposalStatusEnum.REFUSED.name]
        ).select_related('playlist').order_by('-created_at')

    def delete(self, proposal: PlaylistProposal) -> None:
        proposal.delete()
