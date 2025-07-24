
from home.model.SharedSoundboard import SharedSoundboard
from datetime import datetime
from home.utils.logger import LoggerFactory

class SharedSoundboardService(BaseCleanService):
    def __init__(self):
        self.logger = LoggerFactory.get_default_logger()


    def purge_expired_shared_soundboard(self, file_path):
        SharedSoundboard.objects.filter(expiration_date=datetime.now()).delete()
        

