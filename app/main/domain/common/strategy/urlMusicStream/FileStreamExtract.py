from main.domain.common.enum.MusicFormatEnum import MusicFormatEnum
from main.domain.common.enum.LinkMusicTypeEnum import LinkMusicTypeEnum
import requests

from main.domain.common.utils.logger import logger

class FileStreamExtract:
    def __init__(self, link_music):
        self.link_music = link_music

    def extract(self, range_header=None):
        """Extracts data from a file or stream based on the URL type.
        Returns the content of the file or stream if successful, otherwise None.
        """
        if self.link_music.urlType == LinkMusicTypeEnum.FILE.name:
            try:
                self.response = self._get_response(range_header)
                return self._file_generator(self.response), 'file'
            except Exception as e:
                logger.exception(
                    f"[external_stream] file request failed domain={self.link_music.domained_name} "
                    f"url={self.link_music.url}Exception {e}"
                )
                return None, None
        return None, None
        
    def _file_generator(self, response):
        """Generator to yield file content in chunks."""
        try:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        except Exception as e:
            logger.exception(
                f"[external_stream] file read failed domain={self.link_music.domained_name} "
                f"url={self.link_music.url}"
                f"Exception {e}"
            )
            raise
        finally:
            response.close()
        
    def _get_response(self, range_header=None):
        headers = {'Range': range_header} if range_header else None
        response = requests.get(self.link_music.url, headers=headers, stream=True, timeout=10)
        if response.status_code in (200, 206, 416):
            return response
        response.close()
        raise ValueError(f"Failed to retrieve file: {response.status_code}")
        
