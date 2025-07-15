from home.enum.LinkMusicAllowedEnum import LinkMusicAllowedEnum
# from .urlMusicStream... import ...

class UrlMusicStreamStrategy:
    """Fabrique qui retourne la bonne stratégie selon le type de configuration."""
    _strategies = {
    }
    
    def get_strategy(self, domained_name) -> dict:
        if domained_name in self._strategies:
            return self._strategies[domained_name]
        raise ValueError(f"Aucune stratégie trouvée pour le domaine: {domained_name}")