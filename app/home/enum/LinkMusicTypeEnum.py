"""
Énumération des types de liens musicaux.

Définit les différents types de contenus audio externes
supportés par l'application.
"""

from .BaseEnum import BaseEnum

class LinkMusicTypeEnum(BaseEnum):
    """
    Énumération des types de liens musicaux supportés.
    
    Définit les catégories de liens audio externes :
    - FILE : Fichier audio direct
    - STREAM : Flux audio en streaming
    - OTHER : Autre type de contenu
    - ERROR : Lien en erreur ou invalide
    """
    
    FILE = "file"
    STREAM = "stream"
    OTHER = "other"
    ERROR = "error"