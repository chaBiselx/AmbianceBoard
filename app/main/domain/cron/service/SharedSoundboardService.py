
from django.utils import timezone
from main.service.cleanService.BaseCleanService import BaseCleanService
from main.architecture.persistence.models.SharedSoundboard import SharedSoundboard
from main.domain.common.utils.logger import LoggerFactory

class SharedSoundboardService(BaseCleanService):
    def __init__(self):
        self.logger = LoggerFactory.get_default_logger()


    def purge_expired_shared_soundboard(self):
        SharedSoundboard.objects.filter(expiration_date=timezone.now()).delete()
        

