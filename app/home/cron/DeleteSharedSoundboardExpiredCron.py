from home.service.cron.SharedSoundboardService import SharedSoundboardService
from home.utils.logger import logger


def run():
    # code de votre tâche cron
    logger.info("Starting DeleteSharedSoundboardExpiredCron")
    (SharedSoundboardService())
        .purge_expired_shared_soundboard()
    logger.info("Ending DeleteSharedSoundboardExpiredCron")