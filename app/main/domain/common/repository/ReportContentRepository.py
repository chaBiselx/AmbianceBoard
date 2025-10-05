from typing import Any, Optional, List
from main.architecture.persistence.models.ReportContent import ReportContent
from django.db.models import QuerySet


class ReportContentRepository:

    def get(self, id: int) -> ReportContent | None:
        try:
            return ReportContent.objects.get(id=id)
        except ReportContent.DoesNotExist:
            return None

    def get_all_queryset(self, archived: bool) -> QuerySet[ReportContent]:
        return ReportContent.objects.filter(moderator__isnull=archived).order_by('created_at')

