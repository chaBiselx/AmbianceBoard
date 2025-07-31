from main.enum.MusicFormatEnum import MusicFormatEnum
from main.enum.LinkMusicTypeEnum import LinkMusicTypeEnum
import requests

from main.utils.logger import logger

class FileStreamExtract:
    def __init__(self, link_music):
        self.link_music = link_music

    def extract(self):
        """Extracts data from a file or stream based on the URL type.
        Returns the content of the file or stream if successful, otherwise None.
        """
        if self.link_music.urlType == LinkMusicTypeEnum.FILE.name:
            return self._extract_url_file(), 'file'
        return None, None
        
        
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
        response = requests.get(self.link_music.url, stream=True, timeout=10)
        if response.status_code == 200:
            return response
        else:
            raise ValueError(f"Failed to retrieve file: {response.status_code}")
        
