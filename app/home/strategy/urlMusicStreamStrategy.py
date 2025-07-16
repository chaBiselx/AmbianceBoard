from home.enum.LinkMusicAllowedEnum import LinkMusicAllowedEnum
from home.strategy.urlMusicStream.FileStreamExtract import FileStreamExtract

class UrlMusicStreamStrategy:
    """Fabrique qui retourne la bonne stratégie selon le type de configuration."""
    _strategies = {
        LinkMusicAllowedEnum.CUSTOM: FileStreamExtract,
    }
    
    def get_strategy(self, domained_name) -> dict:
        return self._strategies.get(domained_name, FileStreamExtract)
