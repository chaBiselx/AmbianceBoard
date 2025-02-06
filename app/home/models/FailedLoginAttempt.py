from django.db import models
from django.utils import timezone

class FailedLoginAttempt(models.Model):
    ip_address = models.GenericIPAddressField()
    username = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    attempts = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.ip_address} - {self.username}- {self.attempts} attempts"