
from main.domain.cron.service.PurgeUserActivityService import PurgeUserActivityService

from main.domain.common.utils.logger import logger

def run():
    # code de votre tâche cron
    logger.info("Starting PurgeUserActivityCron")
    (PurgeUserActivityService()).purge()
    logger.info("Ending PurgeUserActivityCron")