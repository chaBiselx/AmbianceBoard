class PlaylistDuplicationException(Exception):
    """Exception de base pour les erreurs de duplication de playlist."""
    pass


class PlaylistAlreadyDuplicatedException(PlaylistDuplicationException):
    """Exception levée quand un utilisateur tente de dupliquer une playlist qu'il a déjà dupliquée."""
    
    def __init__(self, playlist_uuid: str, user_username: str, duplicated_at: str):
        """
        Initialise l'exception avec les détails de la duplication existante.
        
        Args:
            playlist_uuid: UUID de la playlist source
            user_username: Nom d'utilisateur qui a déjà dupliqué
            duplicated_at: Date de la première duplication
        """
        self.playlist_uuid = playlist_uuid
        self.user_username = user_username
        self.duplicated_at = duplicated_at
        message = (
            f"L'utilisateur '{user_username}' a déjà dupliqué cette playlist "
            f"(UUID: {playlist_uuid}) le {duplicated_at}"
        )
        super().__init__(message)


class PlaylistNotCopiableException(PlaylistDuplicationException):
    """Exception levée quand une playlist n'est pas marquée comme copiable."""
    
    def __init__(self, playlist_uuid: str, playlist_name: str):
        """
        Initialise l'exception.
        
        Args:
            playlist_uuid: UUID de la playlist
            playlist_name: Nom de la playlist
        """
        self.playlist_uuid = playlist_uuid
        self.playlist_name = playlist_name
        message = f"La playlist '{playlist_name}' (UUID: {playlist_uuid}) n'est pas marquée comme copiable"
        super().__init__(message)
