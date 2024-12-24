import os 
import logging
from django.core.files.storage import default_storage
from ..models.Music import Music

logger = logging.getLogger(__name__)

class MediaAudioService:
    list_media = []
    
    def __init__(self):
        self.media_dir = default_storage.location + "/" + Music.MUSIC_FOLDER
        self.logger = logging.getLogger(__name__)
        
    def clear_media_audio(self):
        self.__get_list_media()
        self.__generate_topic()
        
 
        
    def __get_list_media(self):
        self.list_media =os.listdir(self.media_dir)   
        self.logger.info("NB media files " + str(len(self.list_media)) + "")
        
    def __generate_topic(self):
        for media_file in self.list_media:
            try:
                file_path = Music.MUSIC_FOLDER + media_file
                music_record = Music.objects.filter(file=file_path)
                if not music_record.exists():
                    raise Exception("File not found in the database")
                self.logger.debug(f"File in database: Keep {media_file}")
            except Exception:
                self.logger.debug(f"File not in database: Deleting {media_file}")
                os.remove(default_storage.location + "/" + Music.MUSIC_FOLDER + media_file)

   

    