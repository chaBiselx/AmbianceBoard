import uuid
from django.db import models
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.domain.common.enum.PlaylistProposalStatusEnum import PlaylistProposalStatusEnum


class PlaylistProposal(models.Model):
    """
    Modèle représentant la proposition d'ajout d'une playlist à un soundboard public
    appartenant à un autre utilisateur.

    Un utilisateur (proposer) propose une de ses playlists copiables à un soundboard
    public dont il n'est pas propriétaire. Le propriétaire du soundboard peut accepter
    (la playlist est alors dupliquée via PlaylistDuplicationService et ajoutée au
    soundboard) ou refuser la proposition.
    """

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='proposals')
    soundboard = models.ForeignKey(SoundBoard, on_delete=models.CASCADE, related_name='playlist_proposals')
    proposer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlist_proposals_made')
    status = models.CharField(
        max_length=25,
        choices=[(tag.name, tag.value) for tag in PlaylistProposalStatusEnum],
        default=PlaylistProposalStatusEnum.PENDING.name,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='playlist_proposals_resolved',
    )
    # Playlist résultant de l'acceptation (copie créée pour le propriétaire du soundboard)
    duplicated_playlist = models.ForeignKey(
        Playlist,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proposal_origin',
    )

    class Meta:
        verbose_name = "Proposition de playlist"
        verbose_name_plural = "Propositions de playlist"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['playlist', 'soundboard'], name='unique_playlist_proposal_per_soundboard')
        ]

    def __str__(self) -> str:
        return f"{self.playlist} -> {self.soundboard} ({self.status})"
