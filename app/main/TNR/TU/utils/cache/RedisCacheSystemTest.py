import unittest
import time
from unittest.mock import patch, MagicMock, PropertyMock
from main.domain.common.utils.cache.RedisCacheSystem import RedisCacheSystem
from main.domain.common.utils.cache.ICache import ICache
from django.test import tag
import redis
import pickle


@tag('unitaire')
class RedisCacheSystemTest(unittest.TestCase):
    # Constantes pour les tests
    REDIS_ERROR_MSG = "Connection error"
    
    def setUp(self):
        """Initialisation avant chaque test"""
        # Mock du client Redis
        self.mock_redis = MagicMock(spec=redis.Redis)
        self.cache = RedisCacheSystem()
        
        # Patch de la propriété redis_client
        self.patcher = patch.object(
            RedisCacheSystem, 
            'redis_client', 
            new_callable=PropertyMock,
            return_value=self.mock_redis
        )
        self.patcher.start()

    def tearDown(self):
        """Nettoyage après chaque test"""
        self.patcher.stop()

    def test_set_and_get(self):
        """Test stockage et récupération d'une valeur"""
        # Configuration du mock
        test_value = 'bar'
        serialized = pickle.dumps(test_value)
        self.mock_redis.get.return_value = serialized
        
        # Exécution
        self.cache.set('foo', test_value, timeout=10)
        value = self.cache.get('foo')
        
        # Vérifications
        self.assertEqual(value, test_value)
        self.mock_redis.setex.assert_called_once_with('foo', 10, pickle.dumps(test_value))
        self.mock_redis.get.assert_called_once_with('foo')

    def test_delete(self):
        """Test suppression d'une clé"""
        self.cache.delete('key')
        self.mock_redis.delete.assert_called_once_with('key')

    def test_get_nonexistent_key(self):
        """Test récupération d'une clé inexistante"""
        self.mock_redis.get.return_value = None
        value = self.cache.get('nonexistent_key')
        self.assertIsNone(value)

    def test_delete_nonexistent_key(self):
        """Test suppression d'une clé inexistante - ne doit pas crasher"""
        self.cache.delete('nonexistent_key')
        self.mock_redis.delete.assert_called_once_with('nonexistent_key')

    def test_set_with_custom_timeout(self):
        """Test stockage avec timeout personnalisé"""
        self.cache.set('custom_timeout', 'value', timeout=5)
        self.mock_redis.setex.assert_called_once_with('custom_timeout', 5, pickle.dumps('value'))

    def test_set_with_default_timeout(self):
        """Test stockage avec timeout par défaut (None utilise expiration_duration)"""
        self.cache.set('default_timeout', 'value', timeout=None)
        # Doit appeler setex avec expiration_duration de BaseCache
        args = self.mock_redis.setex.call_args[0]
        self.assertEqual(args[0], 'default_timeout')
        self.assertEqual(args[2], pickle.dumps('value'))

    def test_set_without_timeout(self):
        """Test stockage avec timeout=0 (pas d'expiration)"""
        self.cache.set('no_timeout', 'value', timeout=0)
        # Doit appeler set sans expiration
        self.mock_redis.set.assert_called_once_with('no_timeout', pickle.dumps('value'))

    def test_set_different_types(self):
        """Test stockage de différents types de données"""
        # String
        self.mock_redis.get.return_value = pickle.dumps('string_value')
        self.cache.set('string_key', 'string_value', timeout=10)
        self.assertEqual(self.cache.get('string_key'), 'string_value')
        
        # Integer
        self.mock_redis.get.return_value = pickle.dumps(42)
        self.cache.set('int_key', 42, timeout=10)
        self.assertEqual(self.cache.get('int_key'), 42)
        
        # List
        self.mock_redis.get.return_value = pickle.dumps([1, 2, 3])
        self.cache.set('list_key', [1, 2, 3], timeout=10)
        self.assertEqual(self.cache.get('list_key'), [1, 2, 3])
        
        # Dict
        test_dict = {'a': 1, 'b': 2}
        self.mock_redis.get.return_value = pickle.dumps(test_dict)
        self.cache.set('dict_key', test_dict, timeout=10)
        self.assertEqual(self.cache.get('dict_key'), test_dict)

    def test_overwrite_existing_key(self):
        """Test écrasement d'une valeur existante"""
        self.cache.set('key', 'value1', timeout=10)
        self.cache.set('key', 'value2', timeout=10)
        
        # Vérifie que setex a été appelé deux fois
        self.assertEqual(self.mock_redis.setex.call_count, 2)

    def test_exists(self):
        """Test vérification d'existence d'une clé"""
        self.mock_redis.exists.return_value = 1
        self.assertTrue(self.cache.exists('existing_key'))
        
        self.mock_redis.exists.return_value = 0
        self.assertFalse(self.cache.exists('nonexistent_key'))

    def test_clear(self):
        """Test vidage du cache"""
        self.cache.clear()
        self.mock_redis.flushdb.assert_called_once()

    def test_get_ttl(self):
        """Test récupération du TTL d'une clé"""
        self.mock_redis.ttl.return_value = 300
        ttl = self.cache.get_ttl('key')
        self.assertEqual(ttl, 300)
        
        # Test clé sans TTL (retourne -1)
        self.mock_redis.ttl.return_value = -1
        ttl = self.cache.get_ttl('key_no_ttl')
        self.assertIsNone(ttl)

    def test_get_with_redis_error(self):
        """Test gestion d'erreur Redis lors de la récupération"""
        self.mock_redis.get.side_effect = redis.RedisError(self.REDIS_ERROR_MSG)
        value = self.cache.get('key')
        self.assertIsNone(value)

    def test_set_with_redis_error(self):
        """Test gestion d'erreur Redis lors du stockage"""
        self.mock_redis.setex.side_effect = redis.RedisError(self.REDIS_ERROR_MSG)
        # Ne doit pas lever d'exception
        self.cache.set('key', 'value', timeout=10)

    def test_delete_with_redis_error(self):
        """Test gestion d'erreur Redis lors de la suppression"""
        self.mock_redis.delete.side_effect = redis.RedisError(self.REDIS_ERROR_MSG)
        # Ne doit pas lever d'exception
        self.cache.delete('key')

    def test_get_with_pickle_error(self):
        """Test gestion d'erreur de désérialisation"""
        self.mock_redis.get.return_value = b'invalid_pickle_data'
        
        with patch('pickle.loads', side_effect=pickle.PickleError("Invalid pickle")):
            value = self.cache.get('key')
            self.assertIsNone(value)

    def test_set_with_pickle_error(self):
        """Test gestion d'erreur de sérialisation"""
        with patch('pickle.dumps', side_effect=pickle.PickleError("Cannot pickle")):
            # Ne doit pas lever d'exception
            self.cache.set('key', 'value', timeout=10)

    def test_serialize_deserialize(self):
        """Test des méthodes de sérialisation/désérialisation"""
        test_data = {'key': 'value', 'number': 42, 'list': [1, 2, 3]}
        
        # Test sérialisation
        serialized = self.cache._serialize(test_data)
        self.assertIsInstance(serialized, bytes)
        
        # Test désérialisation
        deserialized = self.cache._deserialize(serialized)
        self.assertEqual(deserialized, test_data)
        
        # Test désérialisation de None
        self.assertIsNone(self.cache._deserialize(None))

    def test_close_connection(self):
        """Test fermeture de la connexion Redis"""
        # Créer une instance avec un mock de client
        cache = RedisCacheSystem()
        cache._redis_client = MagicMock()
        
        cache.close()
        
        cache._redis_client.close.assert_called_once()
        self.assertIsNone(cache._redis_client)

    def test_close_without_connection(self):
        """Test fermeture sans connexion active"""
        cache = RedisCacheSystem()
        cache._redis_client = None
        
        # Ne doit pas lever d'exception
        cache.close()

    def test_is_instance_of_icache(self):
        """Test que RedisCacheSystem implémente ICache"""
        self.assertIsInstance(self.cache, ICache)


@tag('integration')
class RedisCacheSystemIntegrationTest(unittest.TestCase):
    """
    Tests d'intégration avec un vrai serveur Redis.
    Ces tests nécessitent un serveur Redis disponible.
    """
    
    @classmethod
    def setUpClass(cls):
        """Vérifie si Redis est disponible"""
        try:
            cls.cache = RedisCacheSystem()
            cls.cache.redis_client.ping()
            cls.redis_available = True
        except (redis.ConnectionError, redis.RedisError):
            cls.redis_available = False

    def setUp(self):
        """Initialisation avant chaque test"""
        if not self.redis_available:
            self.skipTest("Redis n'est pas disponible")
        self.cache = RedisCacheSystem()
        # Nettoyer avant chaque test
        self.cache.clear()

    def tearDown(self):
        """Nettoyage après chaque test"""
        if self.redis_available:
            self.cache.clear()
            self.cache.close()

    def test_real_set_and_get(self):
        """Test réel de stockage et récupération"""
        self.cache.set('test_key', 'test_value', timeout=10)
        value = self.cache.get('test_key')
        self.assertEqual(value, 'test_value')

    def test_real_timeout(self):
        """Test réel d'expiration (peut être lent)"""
        self.cache.set('timeout_key', 'timeout_value', timeout=1)
        time.sleep(2)
        value = self.cache.get('timeout_key')
        self.assertIsNone(value)

    def test_real_exists(self):
        """Test réel de vérification d'existence"""
        self.cache.set('existing', 'value', timeout=10)
        self.assertTrue(self.cache.exists('existing'))
        self.assertFalse(self.cache.exists('nonexistent'))

    def test_real_ttl(self):
        """Test réel de récupération du TTL"""
        self.cache.set('ttl_key', 'value', timeout=10)
        ttl = self.cache.get_ttl('ttl_key')
        self.assertIsNotNone(ttl)
        self.assertLessEqual(ttl, 10)
        self.assertGreater(ttl, 0)


if __name__ == '__main__':
    unittest.main()
