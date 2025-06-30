import logging
from home.model.SharedSoundboard import SharedSoundboard
from datetime import datetime

class SharedSoundboardService(BaseCleanService):
    def __init__(self):
        self.logger = logging.getLogger('home')


    def purge_expired_shared_soundboard(self, file_path):
        SharedSoundboard.objects.filter(expiration_date=datetime.now()).delete()
        

