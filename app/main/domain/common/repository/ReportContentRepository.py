from typing import Any, Optional, List
from main.architecture.persistence.models.ReportContent import ReportContent


class ReportContentRepository:

    def get(self, id: int) -> ReportContent | None:
        try:
            return ReportContent.objects.get(id=id)
        except ReportContent.DoesNotExist:
            return None

