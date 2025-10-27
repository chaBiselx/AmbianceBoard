from main.domain.cron.service.SharedSoundboardService import SharedSoundboardService
from main.domain.common.utils.logger import logger


def run():
    # code de votre tâche cron
    logger.info("Starting DeleteSharedSoundboardExpiredCron")
    (SharedSoundboardService())\
        .purge_expired_shared_soundboard()
    logger.info("Ending DeleteSharedSoundboardExpiredCron")