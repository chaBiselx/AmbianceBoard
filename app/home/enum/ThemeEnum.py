"""
Énumération des thèmes d'interface utilisateur.

Définit les thèmes visuels disponibles pour l'interface.
"""

from .BaseEnum import BaseEnum

class ThemeEnum(BaseEnum):
    """
    Énumération des thèmes d'interface disponibles.
    
    Définit les options de thème visuel :
    - DARK : Thème sombre
    - LIGHT : Thème clair
    """
    
    DARK = 'dark'
    LIGHT = 'light'