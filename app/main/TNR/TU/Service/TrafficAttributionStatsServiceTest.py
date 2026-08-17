from datetime import date, datetime, timedelta
from django.test import SimpleTestCase, tag

from main.domain.manager.service.TrafficAttributionStatsService import TrafficAttributionStatsService


class FakeTrafficAttributionVisitRepository:
    def __init__(self, rows):
        self._rows = rows

    def get_counts_by_referer_domain(self, start_date, end_date):
        return self._rows


@tag('unitaire')
class TrafficAttributionStatsServiceTest(SimpleTestCase):
    def setUp(self):
        self.service = TrafficAttributionStatsService()

    def test_normalize_referer_domain_keeps_domain_plus_extension(self):
        self.assertEqual('facebook.com', self.service._normalize_referer_domain('l.facebook.com'))
        self.assertEqual('google.com', self.service._normalize_referer_domain('www.google.com'))
        self.assertEqual('example.co.uk', self.service._normalize_referer_domain('m.example.co.uk'))
        self.assertEqual('reddit.com', self.service._normalize_referer_domain('com.reddit.frontpage'))
        self.assertEqual('toplien.fr', self.service._normalize_referer_domain('www.toplien.fr'))
        self.assertEqual('facebook.com', self.service._normalize_referer_domain('i.facebook.com'))
        self.assertEqual('reddit.com', self.service._normalize_referer_domain('ru.reddit.com'))
        self.assertEqual('direct', self.service._normalize_referer_domain('direct'))

    def test_get_referer_data_aggregates_subdomains_on_same_day(self):
        activity_day = date(2026, 8, 10)
        rows = [
            {'referer_domain': 'l.facebook.com', 'date': activity_day, 'count': 2},
            {'referer_domain': 'm.facebook.com', 'date': activity_day, 'count': 3},
            {'referer_domain': 'com.reddit.frontpage', 'date': activity_day, 'count': 4},
            {'referer_domain': 'ru.reddit.com', 'date': activity_day, 'count': 6},
            {'referer_domain': 'www.google.com', 'date': activity_day, 'count': 1},
        ]
        self.service.repository = FakeTrafficAttributionVisitRepository(rows)

        result = self.service.get_referer_data(
            datetime(2026, 8, 1),
            datetime(2026, 8, 31),
        )

        self.assertIn('facebook.com', result['data'])
        self.assertIn('reddit.com', result['data'])
        self.assertIn('google.com', result['data'])
        self.assertEqual(5, result['data']['facebook.com']['data'][0]['count'])
        self.assertEqual(10, result['data']['reddit.com']['data'][0]['count'])
        self.assertEqual(1, result['data']['google.com']['data'][0]['count'])
