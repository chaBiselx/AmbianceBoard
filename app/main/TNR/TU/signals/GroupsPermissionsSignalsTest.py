from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth.models import Group, Permission
from main.architecture.persistence.postMigrate.Group import create_groups
from main.architecture.persistence.postMigrate.Permission import create_permissions, attrib_permissions


class GroupsPermissionsSignalsTest(TestCase):
    """Tests pour les signals post_migrate - création groupes et permissions"""

    @patch('main.architecture.persistence.postMigrate.Group.Settings.get')
    def test_create_groups_idempotent(self, mock_settings_get):
        """Test que create_groups est idempotent - pas de doublons après réexécution"""
        mock_settings_get.return_value = ['ROLE_USER', 'ROLE_ADMIN']
        
        # Première exécution
        create_groups(sender=None)
        groups_count_1 = Group.objects.filter(name__in=['ROLE_USER', 'ROLE_ADMIN']).count()
        
        # Seconde exécution
        create_groups(sender=None)
        groups_count_2 = Group.objects.filter(name__in=['ROLE_USER', 'ROLE_ADMIN']).count()
        
        # Le nombre de groupes ne doit pas changer
        self.assertEqual(groups_count_1, groups_count_2)
        self.assertEqual(groups_count_1, 2)
        
        groups = set(Group.objects.filter(name__in=['ROLE_USER', 'ROLE_ADMIN']).values_list('name', flat=True))
        self.assertSetEqual(groups, {'ROLE_USER', 'ROLE_ADMIN'})

    @patch('main.architecture.persistence.postMigrate.Group.Settings.get')
    def test_create_groups_multiple_executions(self, mock_settings_get):
        """Test multiples exécutions de create_groups - pas de duplication"""
        mock_settings_get.return_value = ['ROLE_USER', 'ROLE_ADMIN', 'ROLE_MODERATOR']
        
        # Trois exécutions
        create_groups(sender=None)
        create_groups(sender=None)
        create_groups(sender=None)
        
        groups_count = Group.objects.filter(name__in=['ROLE_USER', 'ROLE_ADMIN', 'ROLE_MODERATOR']).count()
        self.assertEqual(groups_count, 3)

    @patch('main.architecture.persistence.postMigrate.Group.Settings.get')
    def test_create_groups_empty_list(self, mock_settings_get):
        """Test create_groups avec liste vide - ne crash pas"""
        mock_settings_get.return_value = []
        
        create_groups(sender=None)
        
        # Pas d'erreur levée

    @patch('main.architecture.persistence.postMigrate.Permission.Settings.get')
    def test_create_permissions_and_attrib(self, mock_settings_get):
        """Test création et attribution de permissions"""
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
        perms = set(Permission.objects.filter(codename__in=['can_view', 'can_edit']).values_list('codename', flat=True))
        self.assertSetEqual(perms, {'can_view', 'can_edit'})
        # Attribue
        attrib_permissions(sender=None)
        role_admin = Group.objects.get(name='ROLE_ADMIN')
        role_user = Group.objects.get(name='ROLE_USER')
        self.assertEqual(role_admin.permissions.count(), 2)
        self.assertEqual(role_user.permissions.count(), 1)

    @patch('main.architecture.persistence.postMigrate.Permission.Settings.get')
    def test_create_permissions_idempotent(self, mock_settings_get):
        """Test que create_permissions est idempotent - pas de doublons"""
        mock_settings_get.return_value = {
            'can_view': 'Can View',
            'can_edit': 'Can Edit',
            'can_delete': 'Can Delete'
        }
        
        # Première exécution
        create_permissions(sender=None)
        perms_count_1 = Permission.objects.filter(codename__in=['can_view', 'can_edit', 'can_delete']).count()
        
        # Seconde exécution
        create_permissions(sender=None)
        perms_count_2 = Permission.objects.filter(codename__in=['can_view', 'can_edit', 'can_delete']).count()
        
        # Le nombre de permissions ne doit pas changer
        self.assertEqual(perms_count_1, perms_count_2)
        self.assertEqual(perms_count_1, 3)

    @patch('main.architecture.persistence.postMigrate.Permission.Settings.get')
    def test_attrib_permissions_idempotent(self, mock_settings_get):
        """Test que attrib_permissions est idempotent - pas de doublons d'attribution"""
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
                    }
                }
            if key == 'GROUPS':
                return ['ROLE_ADMIN']
            return []
        mock_settings_get.side_effect = side_effect

        # Setup
        create_groups(sender=None)
        create_permissions(sender=None)
        
        # Première attribution
        attrib_permissions(sender=None)
        role_admin = Group.objects.get(name='ROLE_ADMIN')
        perms_count_1 = role_admin.permissions.count()
        
        # Seconde attribution (reset side_effect)
        mock_settings_get.side_effect = side_effect
        attrib_permissions(sender=None)
        role_admin.refresh_from_db()
        perms_count_2 = role_admin.permissions.count()
        
        # Le nombre de permissions ne doit pas doubler
        self.assertEqual(perms_count_1, perms_count_2)
        self.assertEqual(perms_count_1, 2)

    @patch('main.architecture.persistence.postMigrate.Permission.Settings.get')
    def test_attrib_permissions_with_inheritance(self, mock_settings_get):
        """Test attribution de permissions avec héritage"""
        def side_effect(key):
            if key == 'PERMISSIONS':
                return {
                    'can_view': 'Can View',
                    'can_edit': 'Can Edit',
                    'can_delete': 'Can Delete',
                    'can_admin': 'Can Admin'
                }
            if key == 'ATTRIB_PERMISSIONS':
                return {
                    'ROLE_USER': {
                        'permission': ['can_view'],
                        'inherited_permissions': []
                    },
                    'ROLE_MODERATOR': {
                        'permission': ['can_edit', 'can_delete'],
                        'inherited_permissions': ['ROLE_USER']
                    },
                    'ROLE_ADMIN': {
                        'permission': ['can_admin'],
                        'inherited_permissions': ['ROLE_MODERATOR']
                    }
                }
            if key == 'GROUPS':
                return ['ROLE_USER', 'ROLE_MODERATOR', 'ROLE_ADMIN']
            return []
        mock_settings_get.side_effect = side_effect

        # Setup
        create_groups(sender=None)
        create_permissions(sender=None)
        
        # Attribution avec héritage
        mock_settings_get.side_effect = side_effect
        attrib_permissions(sender=None)
        
        role_user = Group.objects.get(name='ROLE_USER')
        role_moderator = Group.objects.get(name='ROLE_MODERATOR')
        role_admin = Group.objects.get(name='ROLE_ADMIN')
        
        # USER a 1 permission
        self.assertEqual(role_user.permissions.count(), 1)
        self.assertTrue(role_user.permissions.filter(codename='can_view').exists())
        
        # MODERATOR a 2 + 1 héritée = 3
        self.assertEqual(role_moderator.permissions.count(), 3)
        self.assertTrue(role_moderator.permissions.filter(codename='can_view').exists())
        self.assertTrue(role_moderator.permissions.filter(codename='can_edit').exists())
        self.assertTrue(role_moderator.permissions.filter(codename='can_delete').exists())
        
        # ADMIN a 1 + 2 héritées de MODERATOR = 3
        self.assertEqual(role_admin.permissions.count(), 3)
        self.assertTrue(role_admin.permissions.filter(codename='can_admin').exists())
        self.assertTrue(role_admin.permissions.filter(codename='can_edit').exists())
        self.assertTrue(role_admin.permissions.filter(codename='can_delete').exists())

    @patch('main.architecture.persistence.postMigrate.Permission.Settings.get')
    def test_full_workflow_multiple_executions(self, mock_settings_get):
        """Test workflow complet (groups + permissions + attrib) - multiples exécutions"""
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
        
        # Exécution 1
        mock_settings_get.side_effect = side_effect
        create_groups(sender=None)
        create_permissions(sender=None)
        attrib_permissions(sender=None)
        
        groups_count_1 = Group.objects.count()
        perms_count_1 = Permission.objects.filter(codename__in=['can_view', 'can_edit']).count()
        role_admin = Group.objects.get(name='ROLE_ADMIN')
        admin_perms_count_1 = role_admin.permissions.count()
        
        # Exécution 2 (simulate post_migrate signal refiring)
        mock_settings_get.side_effect = side_effect
        create_groups(sender=None)
        create_permissions(sender=None)
        attrib_permissions(sender=None)
        
        groups_count_2 = Group.objects.count()
        perms_count_2 = Permission.objects.filter(codename__in=['can_view', 'can_edit']).count()
        role_admin.refresh_from_db()
        admin_perms_count_2 = role_admin.permissions.count()
        
        # Vérifier aucune duplication
        self.assertEqual(groups_count_1, groups_count_2)
        self.assertEqual(perms_count_1, perms_count_2)
        self.assertEqual(admin_perms_count_1, admin_perms_count_2)
        self.assertEqual(admin_perms_count_1, 2)

    @patch('main.architecture.persistence.postMigrate.Permission.Settings.get')
    def test_create_permissions_empty_dict(self, mock_settings_get):
        """Test create_permissions avec dictionnaire vide - ne crash pas"""
        mock_settings_get.return_value = {}
        
        create_permissions(sender=None)
        
        # Pas d'erreur levée

