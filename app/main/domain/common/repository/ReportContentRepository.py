from typing import Any, Optional, List
from main.architecture.persistence.models.ReportContent import ReportContent
from main.architecture.persistence.models.User import User
from django.db.models import QuerySet


class ReportContentRepository:

    def create(self, type_element: str, uuid_element: str, precision_element: str, description_element: str, creator: Optional[User]) -> ReportContent:
        report = ReportContent.objects.create(
            typeElement=type_element,
            uuidElement=uuid_element,
            precisionElement=precision_element,
            descriptionElement=description_element
        )
        if creator:
            report.creator = creator
        report.save()
        report.refresh_from_db()
        return report

    def get(self, id: int) -> ReportContent | None:
        try:
            return ReportContent.objects.get(id=id)
        except ReportContent.DoesNotExist:
            return None

    def get_all_queryset(self, archived: bool) -> QuerySet[ReportContent]:
        return ReportContent.objects.filter(moderator__isnull=archived).order_by('created_at')

