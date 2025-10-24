import unittest
import unittest.mock
import time
from unittest.mock import patch, MagicMock
from main.domain.common.utils.cache.CacheSystem import CacheSystem
from main.domain.common.utils.cache.CacheFactory import CacheFactory
from main.domain.common.utils.cache.ICache import ICache
from django.test import tag

@tag('unitaire')
class CacheSystemTest(unittest.TestCase):
    def setUp(self):
        self.cache = CacheSystem()

    def test_set_and_get(self):
        self.cache.set('foo', 'bar', timeout=10)
        value = self.cache.get('foo')
        self.assertEqual(value, 'bar')

    def test_delete(self):
        self.cache.set('key', 'value', timeout=10)
        self.cache.delete('key')
        value = self.cache.get('key')
        self.assertIsNone(value)

    def test_timeout(self):
        self.cache.set('timeout_key', 'timeout_value', timeout=1)
        time.sleep(2)
        value = self.cache.get('timeout_key')
        self.assertIsNone(value)

    def test_get_nonexistent_key(self):
        """Test récupération d'une clé inexistante"""
        value = self.cache.get('nonexistent_key')
        self.assertIsNone(value)

    def test_delete_nonexistent_key(self):
        """Test suppression d'une clé inexistante - ne doit pas crasher"""
        self.cache.delete('nonexistent_key')  # Ne devrait pas lever d'exception

    def test_set_with_custom_timeout(self):
        """Test stockage avec timeout personnalisé"""
        self.cache.set('custom_timeout', 'value', timeout=5)
        value = self.cache.get('custom_timeout')
        self.assertEqual(value, 'value')

    def test_set_with_default_timeout(self):
        """Test stockage avec timeout par défaut (None)"""
        self.cache.set('default_timeout', 'value', timeout=None)
        value = self.cache.get('default_timeout')
        self.assertEqual(value, 'value')

    def test_set_different_types(self):
        """Test stockage de différents types de données"""
        # String
        self.cache.set('string_key', 'string_value', timeout=10)
        self.assertEqual(self.cache.get('string_key'), 'string_value')
        
        # Integer
        self.cache.set('int_key', 42, timeout=10)
        self.assertEqual(self.cache.get('int_key'), 42)
        
        # List
        self.cache.set('list_key', [1, 2, 3], timeout=10)
        self.assertEqual(self.cache.get('list_key'), [1, 2, 3])
        
        # Dict
        self.cache.set('dict_key', {'a': 1, 'b': 2}, timeout=10)
        self.assertEqual(self.cache.get('dict_key'), {'a': 1, 'b': 2})

    def test_overwrite_existing_key(self):
        """Test écrasement d'une valeur existante"""
        self.cache.set('key', 'value1', timeout=10)
        self.cache.set('key', 'value2', timeout=10)
        value = self.cache.get('key')
        self.assertEqual(value, 'value2')


@tag('unitaire')
class TestCacheFactory(unittest.TestCase):
    def test_create_memory_cache(self):
        cache = CacheFactory.create_cache('memory')
        self.assertIsInstance(cache, ICache)

    def test_create_invalid_cache(self):
        with self.assertRaises(ValueError):
            CacheFactory.create_cache('invalid')

    def test_create_cache_case_insensitive(self):
        """Test que le type de cache est insensible à la casse"""
        cache = CacheFactory.create_cache('MEMORY')
        self.assertIsInstance(cache, ICache)
        
        cache2 = CacheFactory.create_cache('Memory')
        self.assertIsInstance(cache2, ICache)

    @patch('main.domain.common.utils.cache.CacheFactory.Settings.get')
    def test_get_default_cache(self, mock_settings):
        """Test récupération du cache par défaut depuis Settings"""
        def settings_side_effect(key, default=None):
            if key == 'CACHE_TYPE':
                return 'memory'
            return default
        
        mock_settings.side_effect = settings_side_effect
        
        cache = CacheFactory.get_default_cache()
        
        self.assertIsInstance(cache, ICache)
        # Vérifie que CACHE_TYPE a été appelé
        self.assertIn(unittest.mock.call('CACHE_TYPE'), mock_settings.call_args_list)

    @patch('main.domain.common.utils.cache.CacheFactory.Settings.get')
    def test_get_default_cache_with_invalid_type(self, mock_settings):
        """Test que get_default_cache lève une erreur si type invalide"""
        mock_settings.return_value = 'invalid_type'
        
        with self.assertRaises(ValueError) as context:
            CacheFactory.get_default_cache()
        
        self.assertIn('invalid_type', str(context.exception))

if __name__ == '__main__':
    unittest.main()
