from datetime import timedelta

from django.utils import timezone

from main.domain.common.utils.logger import LoggerFactory
from main.architecture.persistence.repository.UserActivityRepository import UserActivityRepository
from main.architecture.persistence.repository.TrafficAttributionVisitRepository import TrafficAttributionVisitRepository
from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum

class PurgeOldStatsService:
    
    def __init__(self):
        self.logger = LoggerFactory.get_default_logger()
        self.user_activity_repository = UserActivityRepository()
        self.traffic_attribution_visit_repository = TrafficAttributionVisitRepository()
        self.days_older = 366  # Default to 366 days, can be overridden in _purge_old method
        self.days_error = 30  # Default to 30 days, can be overridden in purge_error method

    def set_days_older(self, days: int):
        """
        Set the number of days to keep user activities.
        """
        self.days_older = days
        
    def purge(self):
        self._purge_old()
        self._purge_old_traffic_attribution_visits()
        self._purge_error_log()

    def _purge_queryset(self, queryset, success_message: str, empty_message: str, error_message: str):
        try:
            if queryset.exists():
                deleted_count = queryset.count()
                queryset.delete()
                self.logger.info(success_message.format(count=deleted_count))
            else:
                self.logger.info(empty_message)
        except Exception as e:
            self.logger.error(f"{error_message}: {e}")

    def _purge_old(self):
        """Purge user activities older than a certain number of days"""
        threshold_date = timezone.now() - timedelta(days=self.days_older)
        old_activities = self.user_activity_repository.get_activity_before(threshold_date)
        self._purge_queryset(
            queryset=old_activities,
            success_message="Purged {count} old user activities.",
            empty_message="No old user activities to purge.",
            error_message="Error during purge",
        )

    def _purge_old_traffic_attribution_visits(self):
        """Purge traffic attribution visits older than a certain number of days"""
        threshold_date = timezone.now() - timedelta(days=self.days_older)
        old_visits = self.traffic_attribution_visit_repository.get_visits_before(threshold_date)
        self._purge_queryset(
            queryset=old_visits,
            success_message="Purged {count} old traffic attribution visits.",
            empty_message="No old traffic attribution visits to purge.",
            error_message="Error during traffic attribution purge",
        )
            
    def _purge_error_log(self):
        """Purge user activities related to errors older than a certain number of days"""
        threshold_date = timezone.now() - timedelta(days=self.days_error)
        error_activities = self.user_activity_repository.get_activity_before_with_type(
            threshold_date,
            activity_type=[e.value for e in UserActivityTypeEnum.listing_errors().values()],
        )
        self._purge_queryset(
            queryset=error_activities,
            success_message="Purged {count} old error user activities.",
            empty_message="No old error user activities to purge.",
            error_message="Error during error log purge",
        )

    