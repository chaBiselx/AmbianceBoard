import unittest
import time
from main.utils.cache.CacheSystem import CacheSystem
from main.utils.cache.CacheFactory import CacheFactory
from main.utils.cache.ICache import ICache

class TestCacheSystem(unittest.TestCase):
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


class TestCacheFactory(unittest.TestCase):
    def test_create_memory_cache(self):
        cache = CacheFactory.create_cache('memory')
        self.assertIsInstance(cache, ICache)

    def test_create_invalid_cache(self):
        with self.assertRaises(ValueError):
            CacheFactory.create_cache('invalid')

if __name__ == '__main__':
    unittest.main()
