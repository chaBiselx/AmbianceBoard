from datetime import datetime
from main.architecture.persistence.repository.TrafficAttributionVisitRepository import TrafficAttributionVisitRepository
from main.domain.common.service.BaseActivityStatsService import BaseActivityStatsService


class TrafficAttributionStatsService(BaseActivityStatsService):
    """Service manager pour les graphes d'attribution referer/UTM."""

    # Suffixes publics courants qui utilisent 2 niveaux (co.uk, com.au, etc.)
    MULTI_LEVEL_PUBLIC_SUFFIXES = {
        'co.uk',
        'org.uk',
        'gov.uk',
        'ac.uk',
        'com.au',
        'net.au',
        'org.au',
        'com.br',
        'com.ar',
        'com.mx',
        'com.tr',
        'co.jp',
        'co.kr',
        'co.nz',
        'com.sg',
        'com.hk',
        'com.cn',
        'com.tw',
        'co.za',
    }

    COMMON_TOP_LEVEL_DOMAINS = {
        'com',
        'org',
        'net',
        'io',
        'fr',
        'de',
        'es',
        'it',
        'uk',
        'jp',
        'br',
        'ru',
        'cn',
        'tw',
        'au',
        'ca',
    }

    def __init__(self) -> None:
        self.repository = TrafficAttributionVisitRepository()

    def _normalize_referer_domain(self, referer_domain: str) -> str:
        """Réduit un host au format domaine+extension (ex: l.facebook.com -> facebook.com)."""
        domain = (referer_domain or '').strip().lower()
        if not domain:
            return 'direct'

        if domain in {'direct', 'internal'}:
            return domain

        # Garde tel quel pour les IP ou hôtes non standards
        if domain.replace('.', '').isdigit() or '.' not in domain:
            return domain

        parts = [part for part in domain.split('.') if part]
        if len(parts) < 2:
            return domain

        # Certains clients remontent un package Android (ex: com.reddit.frontpage).
        if len(parts) >= 3 and parts[0] in self.COMMON_TOP_LEVEL_DOMAINS:
            return f'{parts[1]}.{parts[0]}'

        suffix = '.'.join(parts[-2:])
        if suffix in self.MULTI_LEVEL_PUBLIC_SUFFIXES and len(parts) >= 3:
            return '.'.join(parts[-3:])

        return suffix

    def get_referer_data(self, start_date: datetime, end_date: datetime) -> dict:
        rows = self.repository.get_counts_by_referer_domain(start_date, end_date)
        aggregated_rows = {}

        for row in rows:
            normalized_domain = self._normalize_referer_domain(row.get('referer_domain') or 'direct')
            date = row.get('date')
            count = row.get('count', 0)
            key = (normalized_domain, date)

            aggregated_rows[key] = aggregated_rows.get(key, 0) + count

        payload = [
            {
                'activity_type': domain,
                'date': date,
                'count': count,
            }
            for (domain, date), count in sorted(aggregated_rows.items(), key=lambda item: (item[0][1], item[0][0]))
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
