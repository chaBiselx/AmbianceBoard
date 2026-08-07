from datetime import datetime
from main.architecture.persistence.repository.TrafficAttributionVisitRepository import TrafficAttributionVisitRepository
from main.domain.common.service.BaseActivityStatsService import BaseActivityStatsService


class TrafficAttributionStatsService(BaseActivityStatsService):
    """Service manager pour les graphes d'attribution referer/UTM."""

    def __init__(self) -> None:
        self.repository = TrafficAttributionVisitRepository()

    def get_referer_data(self, start_date: datetime, end_date: datetime) -> dict:
        rows = self.repository.get_counts_by_referer_domain(start_date, end_date)
        payload = [
            {
                'activity_type': row.get('referer_domain') or 'direct',
                'date': row.get('date'),
                'count': row.get('count', 0),
            }
            for row in rows
        ]
        return self._generated_line_graph_data(start_date, end_date, payload)

    def get_utm_source_data(self, start_date: datetime, end_date: datetime) -> dict:
        rows = self.repository.get_counts_by_utm_source(start_date, end_date)
        payload = [
            {
                'activity_type': row.get('utm_source') or 'sans_utm_source',
                'date': row.get('date'),
                'count': row.get('count', 0),
            }
            for row in rows
        ]
        return self._generated_line_graph_data(start_date, end_date, payload)
