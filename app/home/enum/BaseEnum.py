"""
Énumération de base pour tous les enums du projet.

Fournit des méthodes utilitaires communes pour toutes les énumérations.
"""

from enum import Enum
from typing import List, Dict, Any

class BaseEnum(Enum):
    """
    Classe de base pour toutes les énumérations du projet.
    
    Fournit des méthodes utilitaires pour convertir les énumérations
    en listes ou dictionnaires.
    """
    
    @classmethod
    def values(cls) -> List[Any]:
        """
        Retourne une liste des valeurs de l'énumération.
        
        Returns:
            List[Any]: Liste des valeurs de l'énumération
        """
        return [c.value for c in cls]
    
    @classmethod
    def convert_to_dict(cls) -> Dict[str, Any]:
        """
        Convertit l'énumération en dictionnaire.
        
        Returns:
            Dict[str, Any]: Dictionnaire avec les noms comme clés et valeurs comme valeurs
        """
        return {c.name: c.value for c in cls}