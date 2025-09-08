"""
Énumération de base pour tous les enums du projet.

Fournit des méthodes utilitaires communes pour toutes les énumérations.
"""

from enum import Enum
from typing import List, Dict, Any


class BaseEnum(str, Enum):
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
    
    @classmethod
    def convert_to_choices(cls) -> List[tuple]:
        """
        Convertit l'énumération en liste de tuples pour les choix (label, value).
        
        Returns:
            List[tuple]: Liste de tuples avec le nom comme label et la valeur comme valeur
        """
        return [(c.value, c.name) for c in cls]
    
    def __json__(self):
        """
        Méthode pour la sérialisation JSON.
        
        Returns:
            str: Valeur de l'énumération pour JSON
        """
        return self.value

    def __str__(self) -> str:
        """Return the string value for printing and JSON serialization helpers."""
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"

