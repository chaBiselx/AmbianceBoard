
import requests
from main.enum.LinkMusicAllowedEnum import LinkMusicAllowedEnum
from main.enum.LinkMusicTypeEnum import LinkMusicTypeEnum
from main.enum.MusicFormatEnum import MusicFormatEnum
from main.strategy.urlMusicStream.FileStreamExtract import FileStreamExtract
from main.strategy.urlMusicStream.InfiniteStreamExtract import InfiniteStreamExtract
from main.utils.logger import logger


class UrlMusicStreamStrategy:
    """Fabrique qui retourne la bonne stratégie selon le type de configuration."""
    _strategies = {
        LinkMusicAllowedEnum.CUSTOM: FileStreamExtract,
    }
    
    def get_strategy(self, link_music) -> dict:
        """Retourne la stratégie appropriée en fonction du domaine du lien."""
        specific = self._strategies.get(link_music.domained_name, None)
        if specific is not None:
            return specific
        self.link_music = link_music
        type_detected =  self._get_type()
        if type_detected == LinkMusicTypeEnum.FILE.name:
            return FileStreamExtract
        if type_detected == LinkMusicTypeEnum.STREAM.name:
            return InfiniteStreamExtract
        raise ValueError(f"Aucune stratégie trouvée pour le type: {type_detected}")
        
        
    
    def _get_type(self):
        type_detected = None
        if self.link_music.urlType is None or self.link_music.urlType == '':
            type_detected = self._detect_type()
            self.link_music.urlType = type_detected
            self.link_music.save()
        else : 
            type_detected = self.link_music.urlType
        return type_detected
    
    def _detect_type(self):
        try:
            list_ext = MusicFormatEnum.values() 

            # Envoyer une requête HEAD pour ne pas télécharger tout le contenu
            response = requests.head(self.link_music.url, allow_redirects=True, timeout=10)

            content_type = response.headers.get("Content-Type", "").lower()
            content_disp = response.headers.get("Content-Disposition", "").lower()
            
            # CAS A : Vérifie si c'est un fichier "normal" (type binaire ou document)
            if "attachment" in content_disp or any(ext in self.link_music.url.lower() for ext in list_ext):
                return LinkMusicTypeEnum.FILE.name
            
            # CAS B : Vérifie si c'est un flux audio
            if "audio" in content_type or "stream" in content_type:
                return LinkMusicTypeEnum.STREAM.name

        except Exception as e:
            logger.warning(f"An error occurred while detecting the URL type: {e}")
            return LinkMusicTypeEnum.ERROR.name
        return LinkMusicTypeEnum.OTHER.name
