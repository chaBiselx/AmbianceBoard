from typing import Any, Optional, List
from main.models.FailedLoginAttempt import FailedLoginAttempt
from django.utils import timezone


class FailedLoginAttemptRepository:

    def get_or_create(self, ip_address: str, username: str, defaults=None) -> tuple[FailedLoginAttempt, bool]:
        if defaults is None:
            defaults = {'timestamp': timezone.now()}
        
        return FailedLoginAttempt.objects.get_or_create(
            ip_address=ip_address,
            username=username,
            defaults=defaults
        )

    def get(self, ip_address: str, username: str) -> FailedLoginAttempt|None:
        return FailedLoginAttempt.objects.filter(ip_address=ip_address, username=username).first()

    def delete(self, ip_address: str, username: str) -> None:
        FailedLoginAttempt.objects.filter(ip_address=ip_address, username=username).delete()