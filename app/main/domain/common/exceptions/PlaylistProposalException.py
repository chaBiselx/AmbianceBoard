class PlaylistProposalException(Exception):
    """Exception de base pour les erreurs de proposition de playlist."""
    pass


class PlaylistProposalAlreadyExistsException(PlaylistProposalException):
    """Exception levée quand une proposition existe déjà pour cette playlist et ce soundboard."""

    def __init__(self, playlist_uuid: str, soundboard_uuid: str):
        self.playlist_uuid = playlist_uuid
        self.soundboard_uuid = soundboard_uuid
        message = (
            f"Une proposition existe déjà pour la playlist (UUID: {playlist_uuid}) "
            f"sur ce soundboard (UUID: {soundboard_uuid})"
        )
        super().__init__(message)


class PlaylistProposalNotEligibleException(PlaylistProposalException):
    """Exception levée quand la playlist n'est pas éligible à la proposition (non copiable, bannie...)."""

    def __init__(self, playlist_uuid: str, playlist_name: str):
        self.playlist_uuid = playlist_uuid
        self.playlist_name = playlist_name
        message = f"La playlist '{playlist_name}' (UUID: {playlist_uuid}) n'est pas éligible à la proposition"
        super().__init__(message)


class PlaylistProposalNotFoundException(PlaylistProposalException):
    """Exception levée quand la proposition n'existe pas."""
    pass


class PlaylistProposalUnauthorizedException(PlaylistProposalException):
    """Exception levée quand l'utilisateur n'est pas autorisé à effectuer cette action."""
    pass


class PlaylistProposalInvalidStatusException(PlaylistProposalException):
    """Exception levée quand la proposition n'est pas dans un statut valide pour l'action demandée."""

    def __init__(self, proposal_uuid: str, current_status: str):
        self.proposal_uuid = proposal_uuid
        self.current_status = current_status
        message = (
            f"La proposition (UUID: {proposal_uuid}) n'est pas dans un état valide pour cette action "
            f"(statut actuel: {current_status})"
        )
        super().__init__(message)
