"""
Énumération des messages d'erreur standardisés.

Définit les messages d'erreur utilisés dans l'application
pour une gestion cohérente des erreurs.
"""
from django.utils.translation import gettext, gettext_noop


from .BaseEnum import BaseEnum

class ErrorMessageEnum(BaseEnum):
    """
    Énumération des messages d'erreur standardisés.
    
    Définit les messages d'erreur couramment utilisés :
    - Erreurs de méthodes HTTP
    - Erreurs de serveur
    - Erreurs de contenu non trouvé
    """
    
    METHOD_NOT_SUPPORTED = gettext_noop('error.method_not_supported')
    NOT_ACCEPTABLE = gettext_noop('error.not_acceptable')
    INTERNAL_SERVER_ERROR = gettext_noop('error.internal_server_error')
    INVALID_REQUEST_METHOD = gettext_noop('error.invalid_request_method')
    ELEMENT_NOT_FOUND = gettext_noop('error.element_not_found')
    DATA_RECUPERATION = gettext_noop('error.data_retrieval')
    PLAYLIST_ALREADY_EXISTS_IN_SOUNDBOARD = gettext_noop(
        'error.playlist_already_exists_in_soundboard'
    )
    SCRIPT_NOT_FOUND = gettext_noop('error.script_not_found')

    def trad(self) -> str:
        """
        Retourne la traduction du message d'erreur.

        Utilise le système de traduction de Django pour localiser le message.
        """
        return gettext(self.value)