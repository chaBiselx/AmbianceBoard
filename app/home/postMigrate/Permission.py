from django.db import migrations
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def create_permissions(sender, **kwargs): # NOSONAR
    content_type = ContentType.objects.get_for_model(Permission)
    
    for codename, label in settings.PERMISSIONS.items():
        Permission.objects.get_or_create(codename=codename, name=label, content_type=content_type)
        
def attrib_permissions(sender, **kwargs): # NOSONAR
    for role, obj in settings.ATTRIB_PERMISSIONS.items():
        group = Group.objects.get(name=role)
        for permission_codename in obj["permission"]:
            permission = Permission.objects.get(codename=permission_codename)
            group.permissions.add(permission)
        
        for inherited_permissions in obj["inherited_permissions"]:
            for permission_codename in settings.ATTRIB_PERMISSIONS[inherited_permissions]["permission"]:
                permission = Permission.objects.get(codename=permission_codename)
                group.permissions.add(permission)

