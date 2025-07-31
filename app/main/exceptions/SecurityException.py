
"""
Exception pour les violations de sécurité.

Exception levée lorsqu'une violation de sécurité est détectée
dans l'application (accès non autorisé, manipulation de données, etc.).
"""

class SecurityException(Exception):
    """
    Exception levée en cas de violation de sécurité.
    
    Utilisée pour signaler les tentatives d'accès non autorisé,
    de manipulation de données ou autres violations de sécurité.
    """
    
    def __init__(self, message: str) -> None:
        """
        Initialise l'exception avec un message descriptif.
        
        Args:
            message: Description de la violation de sécurité
        """
        super().__init__(message)
