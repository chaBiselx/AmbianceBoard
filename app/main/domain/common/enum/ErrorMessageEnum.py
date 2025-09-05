"""
Énumération des messages d'erreur standardisés.

Définit les messages d'erreur utilisés dans l'application
pour une gestion cohérente des erreurs.
"""

from .BaseEnum import BaseEnum

class ErrorMessageEnum(BaseEnum):
    """
    Énumération des messages d'erreur standardisés.
    
    Définit les messages d'erreur couramment utilisés :
    - Erreurs de méthodes HTTP
    - Erreurs de serveur
    - Erreurs de contenu non trouvé
    """
    
    METHOD_NOT_SUPPORTED = 'Méthode non supportée.'
    NOT_ACCEPTABLE = 'non accetable.'
    INTERNAL_SERVER_ERROR = 'une erreur est survenue.'
    INVALID_REQUEST_METHOD = 'Invalid request method.'
    ELEMENT_NOT_FOUND = 'Element introuvable.'
    DATA_RECUPERATION = 'Erreur lors de la récupération des données'