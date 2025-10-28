from typing import Any, Optional, List


from main.architecture.persistence.models.DomainBlacklist import DomainBlacklist

class DomainBlacklistRepository:

    def bulk_create(self, new_domains: List[DomainBlacklist]) -> List[DomainBlacklist]:
        return DomainBlacklist.objects.bulk_create(new_domains, ignore_conflicts=True)
