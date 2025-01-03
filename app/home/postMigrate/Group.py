from django.db import migrations
from django.conf import settings
from django.contrib.auth.models import Group

def create_groups(sender, **kwargs):
    for group in settings.GROUPS:
        Group.objects.get_or_create(name=group)

