

from django.db.models.signals import post_migrate
from main.postMigrate.Group import create_groups
from main.postMigrate.Permission import create_permissions,  attrib_permissions


# Connecter le signal
post_migrate.connect(create_groups)
post_migrate.connect(create_permissions)
post_migrate.connect(attrib_permissions)