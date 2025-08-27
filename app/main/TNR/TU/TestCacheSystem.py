import unittest
from app.main.domain.common.utils.cache.CacheSystem import CacheSystem
from app.main.domain.common.utils.cache.CacheFactory import CacheFactory
from app.main.domain.common.utils.cache.ICache import ICache

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

    def test_cache_name(self):
        self.assertEqual(self.cache.cache_name, 'default')

class TestCacheFactory(unittest.TestCase):
    def test_create_memory_cache(self):
        cache = CacheFactory.create_cache('memory')
        self.assertIsInstance(cache, ICache)

    def test_create_invalid_cache(self):
        with self.assertRaises(ValueError):
            CacheFactory.create_cache('invalid')

if __name__ == '__main__':
    unittest.main()
