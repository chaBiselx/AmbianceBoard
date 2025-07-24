from enum import Enum

class BaseEnum(Enum):
    
    @classmethod
    def values(cls):
        """Retourne une liste des valeurs de l'énumération."""
        return [c.value for c in cls]
    
    @classmethod
    def convert_to_dict(cls):
        """Convertit l'énumération en dictionnaire."""
        return {c.name: c.value for c in cls}