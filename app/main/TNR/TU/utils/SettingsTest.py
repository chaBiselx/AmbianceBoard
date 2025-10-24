import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from main.domain.common.utils.settings import Settings, AppSettings


class SettingsTest(TestCase):
    """Tests pour le wrapper Settings - accès aux configurations"""

    def test_settings_is_app_settings_instance(self):
        """Test que Settings est une instance d'AppSettings"""
        self.assertIsInstance(Settings, AppSettings)

    @override_settings(TEST_SETTING='test_value')
    def test_get_existing_setting(self):
        """Test récupération d'un setting existant"""
        value = Settings.get('TEST_SETTING')
        
        self.assertEqual(value, 'test_value')

    def test_get_nonexistent_setting_with_default(self):
        """Test récupération avec valeur par défaut si setting n'existe pas"""
        value = Settings.get('NONEXISTENT_SETTING', 'default_value')
        
        self.assertEqual(value, 'default_value')

    def test_get_nonexistent_setting_without_default(self):
        """Test récupération sans défaut retourne None"""
        value = Settings.get('NONEXISTENT_SETTING')
        
        self.assertIsNone(value)

    @override_settings(INT_SETTING=42)
    def test_get_integer_setting(self):
        """Test récupération d'un setting de type entier"""
        value = Settings.get('INT_SETTING')
        
        self.assertEqual(value, 42)
        self.assertIsInstance(value, int)

    @override_settings(BOOL_SETTING=True)
    def test_get_boolean_setting(self):
        """Test récupération d'un setting de type booléen"""
        value = Settings.get('BOOL_SETTING')
        
        self.assertTrue(value)
        self.assertIsInstance(value, bool)

    @override_settings(LIST_SETTING=['item1', 'item2', 'item3'])
    def test_get_list_setting(self):
        """Test récupération d'un setting de type liste"""
        value = Settings.get('LIST_SETTING')
        
        self.assertEqual(value, ['item1', 'item2', 'item3'])
        self.assertIsInstance(value, list)

    @override_settings(DICT_SETTING={'key1': 'value1', 'key2': 'value2'})
    def test_get_dict_setting(self):
        """Test récupération d'un setting de type dictionnaire"""
        value = Settings.get('DICT_SETTING')
        
        self.assertEqual(value, {'key1': 'value1', 'key2': 'value2'})
        self.assertIsInstance(value, dict)

    def test_get_with_none_as_default(self):
        """Test que None peut être utilisé comme valeur par défaut explicite"""
        value = Settings.get('NONEXISTENT', None)
        
        self.assertIsNone(value)

    def test_get_with_empty_string_as_default(self):
        """Test qu'une chaîne vide peut être utilisée comme défaut"""
        value = Settings.get('NONEXISTENT', '')
        
        self.assertEqual(value, '')

    @override_settings(EMPTY_STRING_SETTING='')
    def test_get_empty_string_setting(self):
        """Test récupération d'un setting configuré avec chaîne vide"""
        value = Settings.get('EMPTY_STRING_SETTING')
        
        self.assertEqual(value, '')

    @override_settings(ZERO_SETTING=0)
    def test_get_zero_setting(self):
        """Test récupération d'un setting configuré avec 0"""
        value = Settings.get('ZERO_SETTING')
        
        self.assertEqual(value, 0)

    @override_settings(FALSE_SETTING=False)
    def test_get_false_setting(self):
        """Test récupération d'un setting configuré avec False"""
        value = Settings.get('FALSE_SETTING')
        
        self.assertFalse(value)


class AppSettingsTest(TestCase):
    """Tests pour la classe AppSettings"""

    def setUp(self):
        """Configuration initiale des tests"""
        self.settings = AppSettings()

    @override_settings(APP_TEST='app_value')
    def test_app_settings_get(self):
        """Test que AppSettings.get fonctionne correctement"""
        value = self.settings.get('APP_TEST')
        
        self.assertEqual(value, 'app_value')

    def test_app_settings_get_with_default(self):
        """Test AppSettings.get avec valeur par défaut"""
        value = self.settings.get('NONEXISTENT', 'my_default')
        
        self.assertEqual(value, 'my_default')

    def test_get_surcharge_settings_returns_none_by_default(self):
        """Test que _get_surcharge_settings retourne None par défaut (non implémenté)"""
        value = self.settings._get_surcharge_settings('ANY_KEY')
        
        self.assertIsNone(value)

    @patch.object(AppSettings, '_get_surcharge_settings')
    @override_settings(OVERRIDABLE_SETTING='original_value')
    def test_surcharge_settings_override(self, mock_surcharge):
        """Test que la surcharge a priorité sur le setting Django"""
        mock_surcharge.return_value = 'overridden_value'
        
        value = self.settings.get('OVERRIDABLE_SETTING')
        
        self.assertEqual(value, 'overridden_value')
        mock_surcharge.assert_called_once_with('OVERRIDABLE_SETTING')

    @patch.object(AppSettings, '_get_surcharge_settings')
    @override_settings(SETTING_WITH_SURCHARGE='django_value')
    def test_surcharge_settings_none_fallback(self, mock_surcharge):
        """Test que si surcharge retourne None, on utilise le setting Django"""
        mock_surcharge.return_value = None
        
        value = self.settings.get('SETTING_WITH_SURCHARGE')
        
        self.assertEqual(value, 'django_value')

    @override_settings(MULTI_INSTANCE_TEST='shared_value')
    def test_multiple_app_settings_instances(self):
        """Test que plusieurs instances d'AppSettings accèdent aux mêmes settings"""
        settings1 = AppSettings()
        settings2 = AppSettings()
        
        value1 = settings1.get('MULTI_INSTANCE_TEST')
        value2 = settings2.get('MULTI_INSTANCE_TEST')
        
        self.assertEqual(value1, value2)
        self.assertEqual(value1, 'shared_value')

    @override_settings(CACHED_SETTING='initial_value')
    def test_settings_not_cached_between_calls(self):
        """Test que les valeurs ne sont pas cachées (accès direct à Django settings)"""
        value1 = self.settings.get('CACHED_SETTING')
        
        # Modifier le setting (simulation)
        with override_settings(CACHED_SETTING='modified_value'):
            value2 = self.settings.get('CACHED_SETTING')
        
        self.assertEqual(value1, 'initial_value')
        self.assertEqual(value2, 'modified_value')


if __name__ == '__main__':
    unittest.main()
