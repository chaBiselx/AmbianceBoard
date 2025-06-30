import logging
from home.service.cron.SharedSoundboardService import SharedSoundboardService


def run():
    # code de votre tâche cron
    logger = logging.getLogger('home')
    logger.info("Starting DeleteSharedSoundboardExpiredCron")
    (SharedSoundboardService())
        .purge_expired_shared_soundboard()
    logger.info("Ending DeleteSharedSoundboardExpiredCron")