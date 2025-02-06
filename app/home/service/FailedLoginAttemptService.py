import logging
from home.models.FailedLoginAttempt import FailedLoginAttempt
from django.utils import timezone
from datetime import timedelta

class FailedLoginAttemptService:
    
    def __init__(self, request, username):
        self.ip_address = request.META.get('REMOTE_ADDR')
        self.username = username
        self.now = timezone.now()
        self.time_threshold = self.now - timedelta(minutes=15)
        self.logger = logging.getLogger(__name__)
        
    def add_or_create_failed_login_attempt(self):
        failed_attempt, created = FailedLoginAttempt.objects.get_or_create(
                ip_address=self.ip_address,
                username=self.username,
                defaults={'timestamp': self.now}
            )
        if not created:
            if failed_attempt.timestamp > self.time_threshold:
                failed_attempt.attempts += 1
                failed_attempt.timestamp = self.now
            else:
                failed_attempt.attempts = 1
                failed_attempt.timestamp = self.now
            failed_attempt.save()
        return self
    def purge(self):
        FailedLoginAttempt.objects.filter(ip_address=self.ip_address, username=self.username).delete()
        return self
    
    def is_timeout(self) -> bool:
        failed_login_list = FailedLoginAttempt.objects.filter(ip_address=self.ip_address, username=self.username)
        if failed_login_list.exists() :
            failed_login = failed_login_list[0]
            if failed_login.attempts > 3 :
                self.logger.critical(f"User {self.username} has been locked out, attempts: {failed_login.attempts}")
                return True
        return False
    
