from django.test import TestCase, tag

from main.architecture.persistence.models.DomainBlacklist import DomainBlacklist
from main.architecture.persistence.repository.DomainBlacklistRepository import DomainBlacklistRepository


@tag('unitaire')
class DomainBlacklistRepositoryTest(TestCase):
    def setUp(self):
        self.repository = DomainBlacklistRepository()

    def test_bulk_create_creates_new_domains(self):
        domains = [
            DomainBlacklist(domain='blocked-one.example'),
            DomainBlacklist(domain='blocked-two.example'),
        ]

        created = self.repository.bulk_create(domains)

        self.assertEqual(len(created), 2)
        self.assertEqual(DomainBlacklist.objects.count(), 2)

    def test_bulk_create_ignores_conflicts(self):
        DomainBlacklist.objects.create(domain='already-blocked.example')

        domains = [
            DomainBlacklist(domain='already-blocked.example'),
            DomainBlacklist(domain='new-blocked.example'),
        ]

        created = self.repository.bulk_create(domains)

        self.assertEqual(len(created), 2)
        self.assertEqual(DomainBlacklist.objects.count(), 2)
        self.assertTrue(DomainBlacklist.objects.filter(domain='new-blocked.example').exists())
