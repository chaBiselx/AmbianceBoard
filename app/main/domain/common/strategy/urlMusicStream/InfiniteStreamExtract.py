
from main.domain.common.enum.MusicFormatEnum import MusicFormatEnum
from main.domain.common.enum.LinkMusicTypeEnum import LinkMusicTypeEnum
import requests

from main.domain.common.utils.logger import logger

class InfiniteStreamExtract:
    def __init__(self, link_music):
        self.link_music = link_music

    def extract(self):
        """Extracts data from a file or stream based on the URL type.
        Returns the content of the file or stream if successful, otherwise None.
        """
        if self.link_music.urlType == LinkMusicTypeEnum.STREAM.name:
            return self.link_music.url, 'redirect'
        return None, None
        
 
        
