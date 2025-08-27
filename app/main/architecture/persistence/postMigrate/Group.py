from typing import Any
from django.db import migrations
from main.utils.settings import Settings
from django.contrib.auth.models import Group
from django.apps import AppConfig

def create_groups(sender: AppConfig, **kwargs: Any) -> None: # NOSONAR
    for group in Settings.get('GROUPS'):
        Group.objects.get_or_create(name=group)

