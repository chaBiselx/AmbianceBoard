from datetime import timedelta
from django.test import TestCase, tag
from django.utils import timezone
from main.architecture.persistence.repository.TrafficAttributionVisitRepository import TrafficAttributionVisitRepository
from main.architecture.persistence.models.TrafficAttributionVisit import TrafficAttributionVisit


@tag('unitaire')
class TrafficAttributionVisitRepositoryTest(TestCase):
    def setUp(self):
        self.repository = TrafficAttributionVisitRepository()

    def test_create_visit(self):
        visit = self.repository.create(
            path='/public/soundboards',
            uri='https://example.test/public/soundboards?utm_source=google',
            referer_url='https://www.google.com/search?q=test',
            referer_domain='www.google.com',
            session_key='session_1',
            utm_data={'utm_source': 'google'},
            utm_source='google',
        )

        self.assertIsNotNone(visit.id)
        self.assertEqual('www.google.com', visit.referer_domain)
        self.assertEqual('google', visit.utm_source)

    def test_get_counts_by_referer_domain(self):
        today = timezone.now()
        yesterday = today - timedelta(days=1)

        visit1 = self.repository.create(
            path='/public/soundboards',
            uri='https://example.test/public/soundboards',
            referer_url='https://www.google.com/search?q=test',
            referer_domain='www.google.com',
            session_key='session_1',
            utm_data={},
            utm_source='',
        )
        visit2 = self.repository.create(
            path='/public/soundboards',
            uri='https://example.test/public/soundboards',
            referer_url='https://www.facebook.com/',
            referer_domain='www.facebook.com',
            session_key='session_2',
            utm_data={},
            utm_source='',
        )

        TrafficAttributionVisit.objects.filter(id=visit1.id).update(visited_at=today)
        TrafficAttributionVisit.objects.filter(id=visit2.id).update(visited_at=yesterday)

        data = list(self.repository.get_counts_by_referer_domain(yesterday - timedelta(days=1), today + timedelta(days=1)))

        domains = [row['referer_domain'] for row in data]
        self.assertIn('www.google.com', domains)
        self.assertIn('www.facebook.com', domains)

    def test_get_counts_by_utm_source(self):
        now = timezone.now()

        visit1 = self.repository.create(
            path='/public/soundboards',
            uri='https://example.test/public/soundboards?utm_source=google',
            referer_url='',
            referer_domain='direct',
            session_key='session_1',
            utm_data={'utm_source': 'google'},
            utm_source='google',
        )
        visit2 = self.repository.create(
            path='/public/soundboards',
            uri='https://example.test/public/soundboards?utm_source=newsletter',
            referer_url='',
            referer_domain='direct',
            session_key='session_2',
            utm_data={'utm_source': 'newsletter'},
            utm_source='newsletter',
        )

        TrafficAttributionVisit.objects.filter(id=visit1.id).update(visited_at=now)
        TrafficAttributionVisit.objects.filter(id=visit2.id).update(visited_at=now)

        data = list(self.repository.get_counts_by_utm_source(now - timedelta(days=1), now + timedelta(days=1)))

        sources = [row['utm_source'] for row in data]
        self.assertIn('google', sources)
        self.assertIn('newsletter', sources)
