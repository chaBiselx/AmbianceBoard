
from main.domain.cron.service.PurgeUserActivityService import PurgeUserActivityService

from main.utils.logger import logger

def run():
    # code de votre tâche cron
    logger.info("Starting PurgeUserActivityCron")
    (PurgeUserActivityService()).purge_old()
    logger.info("Ending PurgeUserActivityCron")