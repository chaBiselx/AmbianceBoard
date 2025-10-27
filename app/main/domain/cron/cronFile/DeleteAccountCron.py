from main.domain.cron.service.RGPDService import RGPDService
from main.domain.common.utils.logger import logger


def run():
    # code de votre tâche cron
    logger.info("Starting DeleteAccountCron")
    RGPDService()\
        .prevent_account_deletion()\
        .delete_inactive_users()\
        .account_auto_deletion_never_login()\
        .prevent_not_confirmed()\
        .delete_not_confirmed()
    logger.info("Ending DeleteAccountCron")