import logging
from home.service.cron.RGPDService import RGPDService


def run():
    # code de votre tâche cron
    logger = logging.getLogger(__name__)
    logger.info("Starting DeleteAccountCron")
    (RGPDService()).delete_inactive_users()
    logger.info("Ending DeleteAccountCron")