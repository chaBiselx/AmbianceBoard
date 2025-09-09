from .BaseEnum import BaseEnum

class DeviseEnum(BaseEnum):
    """
    Énumération des devises supportées par le système.
    """
    EUR = "€"
    
    @classmethod
    def search(cls, value: str):
        """
        Recherche une devise par sa valeur.
        
        Args:
            value (str): La valeur de la devise à rechercher.
        
        Returns:
            DeviseEnum | None: L'instance de DeviseEnum correspondante ou None si non trouvée.
        """
        for item in cls:
            if item.value == value:
                return item
        return cls.EUR
