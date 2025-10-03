
from django.utils import timezone
from main.domain.brokers.service.cleanService.BaseCleanService import BaseCleanService
from main.architecture.persistence.models.SharedSoundboard import SharedSoundboard
from main.domain.common.utils.logger import LoggerFactory

class SharedSoundboardService(BaseCleanService):
    def __init__(self):
        self.logger = LoggerFactory.get_default_logger()


    def purge_expired_shared_soundboard(self):
        # Utiliser une comparaison inclusive (<=) pour éviter les problèmes de microsecondes
        SharedSoundboard.objects.filter(expiration_date__lte=timezone.now()).delete()  #TODO repository

