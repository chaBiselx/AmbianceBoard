from typing import Callable
from django.http import HttpRequest, HttpResponse
from main.domain.common.utils.logger import LoggerFactory
from main.architecture.persistence.models.TrafficAttributionVisit import TrafficAttributionVisit
from main.architecture.persistence.repository.TrafficAttributionVisitRepository import TrafficAttributionVisitRepository


class PublicVisitTrackingMiddleware:
    """Trace les visites HTTP publiques pour l'attribution marketing."""

    SESSION_ALREADY_COUNTED_KEY = 'traffic_attribution_already_counted'

    excluded_prefixes = [
        '/static/',
        '/media/',
        '/admin/',
        '/manager/',
        '/moderator/',
        '/playlist/',
        '/soundBoards/',
        '/accounts/',
        '/set-language/',
        '/trace-user-activity/',
        '/trace-front',
    ]

    excluded_suffixes = (
        '.css', '.js', '.map', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf'
    )

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        self.logger = LoggerFactory.get_default_logger()
        self.repository = TrafficAttributionVisitRepository()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        try:
            if self._should_track(request, response):
                self._track_visit(request)
        except Exception as e:
            self.logger.error(f"Erreur dans PublicVisitTrackingMiddleware: {e}")

        return response

    def _should_track(self, request: HttpRequest, response: HttpResponse) -> bool:
        return all([
            request.method == 'GET',
            response.status_code < 400,
            not self._is_excluded_path(request.path or ''),
            self._is_html_request(request),
            not self._already_counted_in_session(request),
            not self._is_internal_movement(request),
        ])

    def _is_excluded_path(self, path: str) -> bool:
        return path.endswith(self.excluded_suffixes) or any(
            path.startswith(prefix) for prefix in self.excluded_prefixes
        )

    def _is_html_request(self, request: HttpRequest) -> bool:
        accept_header = (request.headers.get('Accept') or '').lower()
        return 'text/html' in accept_header or '*/*' in accept_header

    def _already_counted_in_session(self, request: HttpRequest) -> bool:
        return hasattr(request, 'session') and request.session.get(
            self.SESSION_ALREADY_COUNTED_KEY,
            False,
        )

    def _is_internal_movement(self, request: HttpRequest) -> bool:
        # Ne pas compter les mouvements internes: on ne garde que les arrivees.
        referer_url = request.META.get('HTTP_REFERER', '')
        referer_domain = TrafficAttributionVisit.extract_referer_domain(
            referer_url=referer_url,
            host=request.get_host(),
        )
        return referer_domain == 'internal'

    def _track_visit(self, request: HttpRequest) -> None:
        referer_url = request.META.get('HTTP_REFERER', '')
        referer_domain = TrafficAttributionVisit.extract_referer_domain(
            referer_url=referer_url,
            host=request.get_host(),
        )

        utm_data = {
            key: value
            for key, value in request.GET.items()
            if key.lower().startswith('utm_')
        }

        utm_source = utm_data.get('utm_source', '')

        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key if hasattr(request, 'session') else ''

        self.repository.create(
            path=request.path,
            uri=request.build_absolute_uri(),
            referer_url=referer_url,
            referer_domain=referer_domain,
            session_key=session_key,
            utm_data=utm_data,
            utm_source=utm_source,
            user=user,
        )

        if hasattr(request, 'session'):
            request.session[self.SESSION_ALREADY_COUNTED_KEY] = True
