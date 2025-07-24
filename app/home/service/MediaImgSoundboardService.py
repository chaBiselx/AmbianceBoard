import os 
from home.utils.logger import LoggerFactory
from django.core.files.storage import default_storage
from parameters import settings
from home.models.SoundBoard import SoundBoard
from home.message.MediaImgSoundBoardMessenger import clean_img_files

class MediaImgSoundboardService:
    list_media = []
    
    def __init__(self):
        self.media_dir = default_storage.location + "/" + SoundBoard.SOUNDBOARD_FOLDER
        self.logger = LoggerFactory.get_default_logger()
        
    def clear_media_img(self):
        self.__get_list_media()
        self.__generate_topic()
        
 
        
    def __get_list_media(self):
        self.list_media =os.listdir(self.media_dir)   
        self.logger.info("NB media files " + SoundBoard.__name__ + " : " + str(len(self.list_media)) + "")
        
    def __generate_topic(self):
        list_media_topic = []
        limit = settings.MEDIA_IMG_MESSENGER_NB_MAX_FILE
        for media_file in self.list_media:
            list_media_topic.append(media_file)
            if len(list_media_topic) == limit:
                clean_img_files.apply_async(args=[list_media_topic], queue='default', priority=4 )
                list_media_topic = []
                
        if len(list_media_topic) > 0:
            clean_img_files.apply_async(args=[list_media_topic], queue='default', priority=4)

    