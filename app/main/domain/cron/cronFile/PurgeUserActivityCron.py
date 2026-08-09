
from main.domain.cron.service.PurgeOldStatsService import PurgeOldStatsService

from main.domain.common.utils.logger import logger

def run():
    # code de votre tâche cron
    logger.info("Starting PurgeOldStatsCron")
    (PurgeOldStatsService()).purge()
    logger.info("Ending PurgeOldStatsCron")