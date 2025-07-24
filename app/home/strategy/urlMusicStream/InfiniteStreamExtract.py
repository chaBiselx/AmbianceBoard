import logging
from home.enum.MusicFormatEnum import MusicFormatEnum
from home.enum.LinkMusicTypeEnum import LinkMusicTypeEnum
import requests

logger = logging.getLogger('home')

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
        
 
        
