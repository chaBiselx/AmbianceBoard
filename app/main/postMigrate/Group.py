from typing import Any
from django.db import migrations
from django.conf import settings
from django.contrib.auth.models import Group
from django.apps import AppConfig

def create_groups(sender: AppConfig, **kwargs: Any) -> None: # NOSONAR
    for group in settings.GROUPS:
        Group.objects.get_or_create(name=group)

