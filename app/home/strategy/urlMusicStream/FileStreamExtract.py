import logging
from home.enum.MusicFormatEnum import MusicFormatEnum
from home.enum.LinkMusicTypeEnum import LinkMusicTypeEnum
import requests

logger = logging.getLogger('home')

class FileStreamExtract:
    def __init__(self, track):
        self.track = track

    def extract(self):
        """Extracts data from a file or stream based on the URL type.
        Returns the content of the file or stream if successful, otherwise None.
        """
        type_detected = None
        if not self.track.urlType :
            type_detected = self._detect_type()
            if type_detected == LinkMusicTypeEnum.FILE.value:
                self.track.urlType = type_detected
                self.track.save()
        else : 
            type_detected = self.track.urlType
        
        if type_detected == LinkMusicTypeEnum.FILE.value:
            return self._extract_url_file()
        return None

    def _detect_type(self):
        try:
            list_ext = [ext.value for ext in MusicFormatEnum]

            # Envoyer une requête HEAD pour ne pas télécharger tout le contenu
            response = requests.head(self.track.url, allow_redirects=True, timeout=10)

            content_type = response.headers.get("Content-Type", "").lower()
            content_disp = response.headers.get("Content-Disposition", "").lower()
            
            # CAS 1 : Vérifie si c'est un fichier "normal" (type binaire ou document)
            if "attachment" in content_disp or any(ext in self.track.url.lower() for ext in list_ext):
                return LinkMusicTypeEnum.FILE.value
            
            # CAS B : Vérifie si c'est un flux audio
            if "audio" in content_type or "stream" in content_type:
                return LinkMusicTypeEnum.STREAM.value

        except Exception as e:
            logger.warning(f"An error occurred while detecting the URL type: {e}")
            return LinkMusicTypeEnum.ERROR.value
        return LinkMusicTypeEnum.OTHER.value
        
        
    def _extract_url_file(self):
        """Extracts data from a file."""
        try:
            return self._file_generator(self._get_response())
        except Exception as e:
            logger.error(f"An error occurred while extracting the file: {e}")
            return None
        
    def _file_generator(self, response):
        """Generator to yield file content in chunks."""
        try:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        except Exception as e:
            logger.error(f"An error occurred while generating file content: {e}")
            return None
        
    def _get_response(self):
        response = requests.get(self.track.url, stream=True, timeout=10)
        if response.status_code == 200:
            return response
        else:
            raise ValueError(f"Failed to retrieve file: {response.status_code}")
        
