import requests
from django.db import IntegrityError
from home.models.DomainBlacklist import DomainBlacklist
from home.service.domain_providers.RemoteTextDomainProvider import RemoteTextDomainProvider

from home.utils.logger import logger

class DomainBlacklistCronService:
    domain_provider = [
        RemoteTextDomainProvider(
            url="https://raw.githubusercontent.com/disposable-email-domains/disposable-email-domains/master/disposable_email_blocklist.conf"
        )
    ]


    def sync_blacklist(self):
        """
        Syncs the domain blacklist using a list of domain providers.
        """
        all_domains = set()
        for provider in self.domain_provider:
            try:
                domains = provider.get_domains()
                all_domains.update(domains)
            except Exception as e:
                logger.error(f"Error getting domains from provider {type(provider).__name__}: {e}")

        if not all_domains:
            logger.info("No domains to sync.")
            return

        new_domains = [
            DomainBlacklist(domain=domain)
            for domain in all_domains
        ]

        if new_domains:
            result = DomainBlacklist.objects.bulk_create(new_domains, ignore_conflicts=True)
            logger.info(f"Successfully synced domains. {len(result)} new domains were added.")
