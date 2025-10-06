
from main.domain.common.utils.logger import LoggerFactory
from main.domain.brokers.service.cleanService.BaseCleanService import BaseCleanService
from main.domain.common.repository.SharedSoundboardRepository import SharedSoundboardRepository


class SharedSoundboardService(BaseCleanService):
    def __init__(self):
        self.logger = LoggerFactory.get_default_logger()


    def purge_expired_shared_soundboard(self):
        # Utiliser une comparaison inclusive (<=) pour éviter les problèmes de microsecondes
        SharedSoundboardRepository().delete_expired()

