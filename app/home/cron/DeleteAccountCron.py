import logging
from home.service.cron.RGPDService import RGPDService


def run():
    # code de votre tâche cron
    logger = logging.getLogger('home')
    logger.info("Starting DeleteAccountCron")
    (RGPDService())
        .prevent_account_deletion()
        .delete_inactive_users()
        .account_auto_deletion_never_login()
    logger.info("Ending DeleteAccountCron")