from main.domain.cron.service.MusicLabelerCronService import MusicLabelerCronService
from main.domain.common.utils.logger import logger


def run():
    logger.info("Début du cron MusicLabelerCron")
    try:
        service = MusicLabelerCronService()
        service.dispatch_unlabeled_tracks()
    except Exception as e:
        logger.error(f"Erreur lors du cron MusicLabelerCron: {str(e)}")
    logger.info("Fin du cron MusicLabelerCron")
