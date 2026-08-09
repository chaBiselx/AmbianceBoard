from unittest.mock import Mock
from django.test import TestCase, RequestFactory, tag
from django.http import HttpResponse
from django.contrib.auth.models import AnonymousUser
from main.architecture.middleware.PublicVisitTrackingMiddleware import PublicVisitTrackingMiddleware
from main.architecture.persistence.models.TrafficAttributionVisit import TrafficAttributionVisit
from main.architecture.persistence.models.User import User


@tag('unitaire')
class PublicVisitTrackingMiddlewareTest(TestCase):
    class DummySession(dict):
        def __init__(self, session_key: str):
            super().__init__()
            self.session_key = session_key

    def _build_session(self, session_key: str):
        return self.DummySession(session_key)

    def setUp(self):
        self.factory = RequestFactory()
        self.get_response_mock = Mock()
        self.middleware = PublicVisitTrackingMiddleware(self.get_response_mock)
        self.user = User.objects.create_user(
            username='publictracker',
            email='publictracker@example.com',
            password='testpass123'
        )

    def test_tracks_public_page_visit_with_utm_and_referer(self):
        request = self.factory.get(
            '/public/soundboards?utm_source=google&utm_campaign=summer',
            HTTP_ACCEPT='text/html',
            HTTP_REFERER='https://www.google.com/search?q=ambianceboard'
        )
        request.user = AnonymousUser()
        request.session = self._build_session('sess_anonymous')

        self.get_response_mock.return_value = HttpResponse(status=200)
        self.middleware(request)

        visits = TrafficAttributionVisit.objects.all()
        self.assertEqual(1, visits.count())

        visit = visits.first()
        self.assertEqual('www.google.com', visit.referer_domain)
        self.assertEqual('google', visit.utm_source)
        self.assertEqual('summer', visit.utm_data.get('utm_campaign'))

    def test_tracks_authenticated_public_visit(self):
        request = self.factory.get('/public/', HTTP_ACCEPT='text/html')
        request.user = self.user
        request.session = self._build_session('sess_auth')

        self.get_response_mock.return_value = HttpResponse(status=200)
        self.middleware(request)

        visit = TrafficAttributionVisit.objects.first()
        self.assertIsNotNone(visit)
        self.assertEqual(self.user, visit.user)
        self.assertTrue(visit.is_authenticated)

    def test_does_not_track_non_public_path(self):
        request = self.factory.get('/manager/', HTTP_ACCEPT='text/html')
        request.user = AnonymousUser()
        request.session = self._build_session('sess_manager')

        self.get_response_mock.return_value = HttpResponse(status=200)
        self.middleware(request)

        self.assertEqual(0, TrafficAttributionVisit.objects.count())

    def test_does_not_track_non_html_request(self):
        request = self.factory.get('/public/soundboards', HTTP_ACCEPT='application/json')
        request.user = AnonymousUser()
        request.session = self._build_session('sess_json')

        self.get_response_mock.return_value = HttpResponse(status=200)
        self.middleware(request)

        self.assertEqual(0, TrafficAttributionVisit.objects.count())

    def test_does_not_track_internal_movement(self):
        request = self.factory.get(
            '/public/soundboards',
            HTTP_ACCEPT='text/html',
            HTTP_REFERER='https://testserver/public/'
        )
        request.user = AnonymousUser()
        request.session = self._build_session('sess_internal')

        self.get_response_mock.return_value = HttpResponse(status=200)
        self.middleware(request)

        self.assertEqual(0, TrafficAttributionVisit.objects.count())

    def test_counts_only_once_per_session(self):
        session = self._build_session('sess_once')

        request1 = self.factory.get(
            '/public/soundboards?utm_source=google',
            HTTP_ACCEPT='text/html',
            HTTP_REFERER='https://www.google.com/search?q=ambianceboard'
        )
        request1.user = AnonymousUser()
        request1.session = session

        request2 = self.factory.get(
            '/public/soundboards',
            HTTP_ACCEPT='text/html'
        )
        request2.user = AnonymousUser()
        request2.session = session

        self.get_response_mock.return_value = HttpResponse(status=200)
        self.middleware(request1)
        self.middleware(request2)

        self.assertTrue(session.get(self.middleware.SESSION_ALREADY_COUNTED_KEY, False))
        self.assertEqual(1, TrafficAttributionVisit.objects.count())

    def test_extract_referer_domain_direct_and_internal(self):
        direct = TrafficAttributionVisit.extract_referer_domain('', 'ambianceboard.test')
        internal = TrafficAttributionVisit.extract_referer_domain('https://ambianceboard.test/public/', 'ambianceboard.test')

        self.assertEqual('direct', direct)
        self.assertEqual('internal', internal)
