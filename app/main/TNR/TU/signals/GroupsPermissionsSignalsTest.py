from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth.models import Group, Permission
from main.architecture.persistence.postMigrate.Group import create_groups
from main.architecture.persistence.postMigrate.Permission import create_permissions, attrib_permissions


class GroupsPermissionsSignalsTest(TestCase):

    @patch('main.architecture.persistence.postMigrate.Group.Settings.get')
    def test_create_groups_idempotent(self, mock_settings_get):
        mock_settings_get.return_value = ['ROLE_USER', 'ROLE_ADMIN']
        create_groups(sender=None)
        create_groups(sender=None)  # seconde exécution
        groups = set(Group.objects.filter(name__in=['ROLE_USER','ROLE_ADMIN']).values_list('name', flat=True))
        self.assertSetEqual(groups, {'ROLE_USER', 'ROLE_ADMIN'})

    @patch('main.architecture.persistence.postMigrate.Permission.Settings.get')
    def test_create_permissions_and_attrib(self, mock_settings_get):
        # Simule PERMISSIONS puis ATTRIB_PERMISSIONS selon ordre d'appel
        def side_effect(key):
            if key == 'PERMISSIONS':
                return {
                    'can_view': 'Can View',
                    'can_edit': 'Can Edit'
                }
            if key == 'ATTRIB_PERMISSIONS':
                return {
                    'ROLE_ADMIN': {
                        'permission': ['can_view', 'can_edit'],
                        'inherited_permissions': []
                    },
                    'ROLE_USER': {
                        'permission': ['can_view'],
                        'inherited_permissions': []
                    }
                }
            if key == 'GROUPS':
                return ['ROLE_ADMIN', 'ROLE_USER']
            return []
        mock_settings_get.side_effect = side_effect

        # Crée d'abord les groupes
        create_groups(sender=None)
        # Crée les permissions
        create_permissions(sender=None)
        perms = set(Permission.objects.filter(codename__in=['can_view','can_edit']).values_list('codename', flat=True))
        self.assertSetEqual(perms, {'can_view','can_edit'})
        # Attribue
        attrib_permissions(sender=None)
        role_admin = Group.objects.get(name='ROLE_ADMIN')
        role_user = Group.objects.get(name='ROLE_USER')
        self.assertEqual(role_admin.permissions.count(), 2)
        self.assertEqual(role_user.permissions.count(), 1)
