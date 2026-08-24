from django.db import transaction
from django.utils import timezone
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.PlaylistProposal import PlaylistProposal
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.PlaylistProposalRepository import PlaylistProposalRepository
from main.architecture.persistence.repository.PlaylistDuplicationHistoryRepository import PlaylistDuplicationHistoryRepository
from main.architecture.persistence.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository
from main.domain.common.service.PlaylistDuplicationService import PlaylistDuplicationService
from main.domain.common.service.SoundboardPlaylistService import SoundboardPlaylistService
from main.domain.common.enum.PlaylistProposalStatusEnum import PlaylistProposalStatusEnum
from main.domain.common.exceptions.PlaylistProposalException import (
    PlaylistProposalAlreadyExistsException,
    PlaylistProposalNotEligibleException,
    PlaylistProposalUnauthorizedException,
    PlaylistProposalInvalidStatusException,
)
from main.architecture.messaging.email.UserMail import UserMail
from main.domain.common.utils.cache.CacheFactory import CacheFactory
from main.domain.common.utils.logger import logger


class PlaylistProposalService:
    """
    Service pour gérer le cycle de vie des propositions de playlist sur les
    soundboards publics (proposer, retirer, accepter, refuser, masquer).
    """

    PREFIX_CACHE_NAVBAR_PROPOSALS = "navbar:pending_playlist_proposals:"

    def __init__(self):
        self.proposal_repository = PlaylistProposalRepository()
        self.duplication_history_repository = PlaylistDuplicationHistoryRepository()
        self.soundboard_playlist_repository = SoundboardPlaylistRepository()
        self.cache = CacheFactory.get_default_cache()

    def propose(self, source_playlist: Playlist, target_soundboard: SoundBoard, proposer: User) -> PlaylistProposal:
        """Crée une proposition d'ajout d'une playlist de `proposer` sur le soundboard `target_soundboard`."""
        if not target_soundboard.is_public or target_soundboard.user == proposer:
            raise PlaylistProposalUnauthorizedException("Ce soundboard n'accepte pas de proposition de cet utilisateur")

        if source_playlist.user != proposer:
            raise PlaylistProposalUnauthorizedException("Vous n'êtes pas propriétaire de cette playlist")

        if not source_playlist.is_copiable or source_playlist.moderator_ban_copie:
            raise PlaylistProposalNotEligibleException(str(source_playlist.uuid), source_playlist.name)

        if self.proposal_repository.find_existing(source_playlist, target_soundboard):
            raise PlaylistProposalAlreadyExistsException(str(source_playlist.uuid), str(target_soundboard.uuid))

        playlist_proposal = self.proposal_repository.create(source_playlist, target_soundboard, proposer)

        try:
            UserMail(target_soundboard.user).playlist_proposal_received(playlist_proposal)
        except Exception as exception:
            logger.error(f"Erreur lors de l'envoi de l'email de proposition de playlist: {exception}")

        self._reset_cache_navbar(target_soundboard.user)
        return playlist_proposal

    def withdraw(self, proposal: PlaylistProposal, requester: User) -> None:
        """Retire une proposition PENDING, à l'initiative de son auteur."""
        if proposal.proposer != requester:
            raise PlaylistProposalUnauthorizedException("Vous n'êtes pas l'auteur de cette proposition")
        if proposal.status != PlaylistProposalStatusEnum.PENDING.name:
            raise PlaylistProposalInvalidStatusException(str(proposal.uuid), proposal.status)

        owner = proposal.soundboard.user
        self.proposal_repository.delete(proposal)
        self._reset_cache_navbar(owner)

    def dismiss(self, proposal: PlaylistProposal, requester: User) -> None:
        """Supprime définitivement une proposition REFUSED, à l'initiative de son auteur."""
        if proposal.proposer != requester:
            raise PlaylistProposalUnauthorizedException("Vous n'êtes pas l'auteur de cette proposition")
        if proposal.status != PlaylistProposalStatusEnum.REFUSED.name:
            raise PlaylistProposalInvalidStatusException(str(proposal.uuid), proposal.status)

        self.proposal_repository.delete(proposal)

    def accept(self, proposal: PlaylistProposal, resolver: User) -> Playlist:
        """
        Accepte une proposition PENDING : duplique la playlist source pour `resolver`
        (ou réutilise une duplication existante) et l'ajoute au soundboard cible.
        """
        if proposal.soundboard.user != resolver:
            raise PlaylistProposalUnauthorizedException("Vous n'êtes pas propriétaire de ce soundboard")
        if proposal.status != PlaylistProposalStatusEnum.PENDING.name:
            raise PlaylistProposalInvalidStatusException(str(proposal.uuid), proposal.status)

        with transaction.atomic():
            existing_duplication = self.duplication_history_repository.find_existing_duplication(
                proposal.playlist.uuid, resolver
            )
            if existing_duplication:
                # B a déjà dupliqué cette playlist source ailleurs : on réutilise la copie existante.
                duplicated_playlist = existing_duplication.duplicated_playlist
            else:
                duplicated_playlist = PlaylistDuplicationService(proposal.playlist, resolver).duplicate()

            if not self.soundboard_playlist_repository.get(proposal.soundboard, duplicated_playlist):
                SoundboardPlaylistService(proposal.soundboard).add_default(duplicated_playlist)

            proposal.status = PlaylistProposalStatusEnum.ACCEPTED.name
            proposal.resolved_at = timezone.now()
            proposal.resolved_by = resolver
            proposal.duplicated_playlist = duplicated_playlist
            proposal.save()

        self._reset_cache_navbar(resolver)
        return duplicated_playlist

    def refuse(self, proposal: PlaylistProposal, resolver: User) -> None:
        """Refuse une proposition PENDING."""
        if proposal.soundboard.user != resolver:
            raise PlaylistProposalUnauthorizedException("Vous n'êtes pas propriétaire de ce soundboard")
        if proposal.status != PlaylistProposalStatusEnum.PENDING.name:
            raise PlaylistProposalInvalidStatusException(str(proposal.uuid), proposal.status)

        proposal.status = PlaylistProposalStatusEnum.REFUSED.name
        proposal.resolved_at = timezone.now()
        proposal.resolved_by = resolver
        proposal.save()

        self._reset_cache_navbar(resolver)

    def _reset_cache_navbar(self, owner: User) -> None:
        """Invalide le compteur en cache de propositions en attente affiché dans la navbar."""
        cache_key = f"{self.PREFIX_CACHE_NAVBAR_PROPOSALS}{owner.id}"
        self.cache.delete(cache_key)
