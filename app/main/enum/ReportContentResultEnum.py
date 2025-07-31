"""
Énumération des résultats de modération des signalements.

Définit les différents résultats possibles lors du traitement
d'un signalement de contenu par un modérateur.
"""

from enum import Enum
from django.templatetags.static import static 

class ReportContentResultEnum(Enum):
    """
    Énumération des résultats de modération des signalements.
    
    Définit les différentes décisions qu'un modérateur peut prendre :
    - INVALID : Signalement non fondé
    - VALID : Signalement justifié, contenu à supprimer
    - SPAM : Signalement considéré comme spam
    - DUPLICATE : Signalement en doublon
    - OTHER : Autre raison
    """
    
    INVALID = 'invalid'
    VALID = 'valid'
    SPAM = 'spam'
    DUPLICATE = 'duplicate'
    OTHER = 'other'