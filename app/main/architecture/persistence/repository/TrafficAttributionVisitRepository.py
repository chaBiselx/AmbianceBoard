from datetime import datetime
from typing import Any, Optional
from django.db.models import Count, QuerySet
from django.db.models.functions import TruncDate
from main.architecture.persistence.models.TrafficAttributionVisit import TrafficAttributionVisit
from main.architecture.persistence.models.User import User


class TrafficAttributionVisitRepository:
    """Repository dedie aux visites et agregations d'attribution."""

    def create(
        self,
        path: str,
        uri: str,
        referer_url: str,
        referer_domain: str,
        session_key: str,
        utm_data: dict,
        utm_source: str = "",
        user: Optional[User] = None,
    ) -> TrafficAttributionVisit:
        visit = TrafficAttributionVisit(
            user=user,
            is_authenticated=user is not None and user.is_authenticated,
            path=path or "",
            uri=uri or "",
            referer_url=referer_url or "",
            referer_domain=referer_domain or "direct",
            session_key=session_key or "",
            utm_data=utm_data or {},
            utm_source=utm_source or "",
        )
        visit.save()
        return visit

    def get_visits_before(self, date: datetime) -> QuerySet[TrafficAttributionVisit]:
        return TrafficAttributionVisit.objects.filter(visited_at__lt=date)

    def get_counts_by_referer_domain(self, start_date: datetime, end_date: datetime):
        return (
            TrafficAttributionVisit.objects.filter(visited_at__gte=start_date, visited_at__lte=end_date)
            .annotate(date=TruncDate('visited_at'))
            .values('date', 'referer_domain')
            .annotate(count=Count('id'))
            .order_by('date', 'referer_domain')
        )

    def get_counts_by_utm_source(self, start_date: datetime, end_date: datetime):
        return (
            TrafficAttributionVisit.objects.filter(visited_at__gte=start_date, visited_at__lte=end_date)
            .annotate(date=TruncDate('visited_at'))
            .values('date', 'utm_source')
            .annotate(count=Count('id'))
            .order_by('date', 'utm_source')
        )
