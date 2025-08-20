import os 
from main.utils.logger import LoggerFactory
from main.domain.common.repository.UserActivityRepository import UserActivityRepository

class PurgeUserActivityService:
    
    def __init__(self):
        self.logger = LoggerFactory.get_default_logger()
        self.user_activity_repository = UserActivityRepository()
        self.days = 366  # Default to 366 days, can be overridden in purge_old method

    def set_days(self, days: int):
        """
        Set the number of days to keep user activities.
        """
        self.days = days

    def purge_old(self):
        """Purge user activities older than a certain number of days"""
        try:
            from datetime import datetime, timedelta
            threshold_date = datetime.now() - timedelta(days=self.days)
            old_activities = self.user_activity_repository.get_activity_before(threshold_date)
            if old_activities.exists():
                self.logger.info(f"Purged {old_activities.count()} old user activities.")
                old_activities.delete()
            else:
                self.logger.info("No old user activities to purge.")
        except Exception as e:
            self.logger.error(f"Error during purge: {e}")

    