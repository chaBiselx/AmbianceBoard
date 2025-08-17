import os 
from django.core.files.storage import default_storage
from parameters import settings
from main.models.Music import Music
from main.message.MediaAudioMessenger import clean_audio_messenger
from main.utils.logger import LoggerFactory

class MediaAudioService:
    list_media = []
    
    def __init__(self):
        self.media_dir = default_storage.location + "/" + Music.MUSIC_FOLDER
        self.logger = LoggerFactory.get_default_logger()
        
    def clear_media_audio(self):
        self.__get_list_media()
        self.__generate_topic()
        
 
        
    def __get_list_media(self):
        self.list_media =os.listdir(self.media_dir)   
        self.logger.info("NB media files " + Music.__name__ + " : " + str(len(self.list_media)) + "")
        
    def __generate_topic(self):
        list_media_topic = []
        limit = settings.MEDIA_AUDIO_MESSENGER_NB_MAX_FILE
        for media_file in self.list_media:
            list_media_topic.append(media_file)
            if len(list_media_topic) == limit:
                clean_audio_messenger.apply_async(args=[list_media_topic], queue='default', priority=4 )
                list_media_topic = []
                
        if len(list_media_topic) > 0:
            clean_audio_messenger.apply_async(args=[list_media_topic], queue='default', priority=4)

    