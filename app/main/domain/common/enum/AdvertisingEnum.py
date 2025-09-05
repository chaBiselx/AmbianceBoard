"""

"""

from .BaseEnum import BaseEnum

class AdvertisingEnum(BaseEnum):
    """
    
    """
    
    FULL = "full" # Toutes les publicité
    PARTIAL = "partial" # publicité modéré
    NONE = "none" # Aucune publicité
    
    def get_text_pricing(self) -> str:
        """
        Récupère la classe d'icône FontAwesome pour ce type de playlist.
        
        Returns:
            str: Classe CSS FontAwesome pour l'icône
        """
        default_class ={
            self.FULL.name: "Oui",
            self.PARTIAL.name: "Partielle",
            self.NONE.name: "Aucune"
        }
        return default_class.get(self.name, "fa-solid fa-sliders")
        