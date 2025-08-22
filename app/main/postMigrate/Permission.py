from typing import Any
from django.db import migrations
from main.utils.settings import Settings

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import AppConfig

def create_permissions(sender: AppConfig, **kwargs: Any) -> None: # NOSONAR
    content_type = ContentType.objects.get_for_model(Permission)

    for codename, label in Settings.get('PERMISSIONS').items():
        Permission.objects.get_or_create(codename=codename, name=label, content_type=content_type)
        
def attrib_permissions(sender: AppConfig, **kwargs: Any) -> None: # NOSONAR
    for role, obj in Settings.get('ATTRIB_PERMISSIONS').items():
        group = Group.objects.get(name=role)
        for permission_codename in obj["permission"]:
            permission = Permission.objects.get(codename=permission_codename)
            group.permissions.add(permission)
        
        for inherited_permissions in obj["inherited_permissions"]:
            for permission_codename in settings.ATTRIB_PERMISSIONS[inherited_permissions]["permission"]:
                permission = Permission.objects.get(codename=permission_codename)
                group.permissions.add(permission)

