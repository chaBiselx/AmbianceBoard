import logging
from home.service.cron import DomainBlacklistCronService

logger = logging.getLogger('home')

def run():
    # code de votre tâche cron
    logger.info("Starting SyncDomainBlacklistCron")
    domain_blacklist_cron_service = DomainBlacklistCronService()
    domain_blacklist_cron_service.sync_blacklist()
    logger.info("Ending SyncDomainBlacklistCron")

