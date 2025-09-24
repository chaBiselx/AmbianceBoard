import os 
from main.domain.common.utils.logger import LoggerFactory
from main.domain.common.repository.UserActivityRepository import UserActivityRepository
from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum

class PurgeUserActivityService:
    
    def __init__(self):
        self.logger = LoggerFactory.get_default_logger()
        self.user_activity_repository = UserActivityRepository()
        self.days_older = 366  # Default to 366 days, can be overridden in _purge_old method
        self.days_error = 30  # Default to 30 days, can be overridden in purge_error method

    def set_days_older(self, days: int):
        """
        Set the number of days to keep user activities.
        """
        self.days_older = days
        
    def purge(self):
        self._purge_old()
        self._purge_error_log()

    def _purge_old(self):
        """Purge user activities older than a certain number of days"""
        try:
            from datetime import timedelta
            from django.utils import timezone
            threshold_date = timezone.now() - timedelta(days=self.days_older)
            old_activities = self.user_activity_repository.get_activity_before(threshold_date)
            if old_activities.exists():
                self.logger.info(f"Purged {old_activities.count()} old user activities.")
                old_activities.delete()
            else:
                self.logger.info("No old user activities to purge.")
        except Exception as e:
            self.logger.error(f"Error during purge: {e}")
            
    def _purge_error_log(self):
        """Purge user activities related to errors older than a certain number of days"""
        try:
            from datetime import timedelta
            from django.utils import timezone
            threshold_date = timezone.now() - timedelta(days=self.days_error)
            error_activities = self.user_activity_repository.get_activity_before_with_type(threshold_date, activity_type=[e.value for e in UserActivityTypeEnum.listing_errors().values()])
            if error_activities.exists():
                self.logger.info(f"Purged {error_activities.count()} old error user activities.")
                error_activities.delete()
            else:
                self.logger.info("No old error user activities to purge.")
        except Exception as e:
            self.logger.error(f"Error during error log purge: {e}")

    