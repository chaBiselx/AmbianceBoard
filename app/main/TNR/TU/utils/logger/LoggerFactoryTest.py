"""
Tests unitaires pour LoggerFactory.
Tests de la factory de création de loggers avec différents types et configurations.
"""

import logging
from django.test import TestCase, override_settings
from django.conf import settings
from unittest.mock import patch, MagicMock

from main.utils.logger.LoggerFactory import LoggerFactory
from main.utils.logger.ILogger import ILogger
from main.utils.logger.LoggerFile import LoggerFile
from main.utils.logger.MemoryLogger import MemoryLogger


class LoggerFactoryTestCase(TestCase):
    """Tests pour la factory LoggerFactory"""
    
    def setUp(self):
        """Configuration avant chaque test - Désactiver le logging pour éviter le spam console"""
        # Sauvegarder le niveau de logging actuel
        self.original_logging_level = logging.getLogger().level
        # Désactiver temporairement le logging pour les tests
        logging.disable(logging.CRITICAL)
    
    def tearDown(self):
        """Nettoyage après chaque test - Réactiver le logging"""
        # Réactiver le logging
        logging.disable(logging.NOTSET)
        # Restaurer le niveau original
        logging.getLogger().setLevel(self.original_logging_level)
    
    def test_create_file_logger(self):
        """Test de création d'un LoggerFile"""
        logger = LoggerFactory.create_logger('test_logger', 'file')
        
        self.assertIsInstance(logger, LoggerFile)
        self.assertIsInstance(logger, ILogger)
        self.assertEqual(logger.logger_name, 'test_logger')
    
    def test_create_memory_logger(self):
        """Test de création d'un MemoryLogger"""
        logger = LoggerFactory.create_logger('test_memory', 'memory')
        
        self.assertIsInstance(logger, MemoryLogger)
        self.assertIsInstance(logger, ILogger)
        self.assertEqual(logger.logger_name, 'test_memory')
    
    def test_create_logger_case_insensitive(self):
        """Test que le type de logger est insensible à la casse"""
        logger_file_upper = LoggerFactory.create_logger('test', 'FILE')
        logger_memory_upper = LoggerFactory.create_logger('test', 'MEMORY')
        logger_file_mixed = LoggerFactory.create_logger('test', 'File')
        logger_memory_mixed = LoggerFactory.create_logger('test', 'Memory')
        
        self.assertIsInstance(logger_file_upper, LoggerFile)
        self.assertIsInstance(logger_memory_upper, MemoryLogger)
        self.assertIsInstance(logger_file_mixed, LoggerFile)
        self.assertIsInstance(logger_memory_mixed, MemoryLogger)
    
    def test_create_logger_default_parameters(self):
        """Test de création avec les paramètres par défaut"""
        logger = LoggerFactory.create_logger()
        
        self.assertIsInstance(logger, LoggerFile)
        self.assertEqual(logger.logger_name, 'main')
    
    def test_create_logger_custom_name_default_type(self):
        """Test de création avec nom personnalisé et type par défaut"""
        logger = LoggerFactory.create_logger('custom_logger')
        
        self.assertIsInstance(logger, LoggerFile)
        self.assertEqual(logger.logger_name, 'custom_logger')
    
    def test_create_logger_invalid_type(self):
        """Test avec un type de logger invalide"""
        with self.assertRaises(ValueError) as context:
            LoggerFactory.create_logger('test', 'invalid_type')
        
        error_message = str(context.exception)
        self.assertIn('Type de logger non supporté: invalid_type', error_message)
        self.assertIn("Types supportés: 'file', 'memory'", error_message)
    
    def test_create_logger_empty_type(self):
        """Test avec un type de logger vide"""
        with self.assertRaises(ValueError):
            LoggerFactory.create_logger('test', '')
    
    def test_create_logger_none_type(self):
        """Test avec un type de logger None"""
        with self.assertRaises(AttributeError):
            LoggerFactory.create_logger('test', None)
    
    def test_multiple_loggers_different_names(self):
        """Test de création de plusieurs loggers avec des noms différents"""
        logger1 = LoggerFactory.create_logger('logger1', 'file')
        logger2 = LoggerFactory.create_logger('logger2', 'memory')
        logger3 = LoggerFactory.create_logger('logger3', 'file')
        
        self.assertEqual(logger1.logger_name, 'logger1')
        self.assertEqual(logger2.logger_name, 'logger2')
        self.assertEqual(logger3.logger_name, 'logger3')
        
        self.assertIsInstance(logger1, LoggerFile)
        self.assertIsInstance(logger2, MemoryLogger)
        self.assertIsInstance(logger3, LoggerFile)
    
    def test_multiple_loggers_same_name_different_types(self):
        """Test de création de plusieurs loggers avec le même nom mais types différents"""
        logger_file = LoggerFactory.create_logger('same_name', 'file')
        logger_memory = LoggerFactory.create_logger('same_name', 'memory')
        
        self.assertEqual(logger_file.logger_name, 'same_name')
        self.assertEqual(logger_memory.logger_name, 'same_name')
        
        self.assertIsInstance(logger_file, LoggerFile)
        self.assertIsInstance(logger_memory, MemoryLogger)
        
        # Vérifier qu'ils sont des instances différentes
        self.assertNotEqual(id(logger_file), id(logger_memory))
    
    @override_settings(LOGGER_TYPE='memory')
    def test_get_default_logger_with_memory_setting(self):
        """Test de get_default_logger avec LOGGER_TYPE='memory' dans settings"""
        logger = LoggerFactory.get_default_logger()
        
        self.assertIsInstance(logger, MemoryLogger)
        self.assertEqual(logger.logger_name, 'main')
    
    @override_settings(LOGGER_TYPE='file')
    def test_get_default_logger_with_file_setting(self):
        """Test de get_default_logger avec LOGGER_TYPE='file' dans settings"""
        logger = LoggerFactory.get_default_logger()
        
        self.assertIsInstance(logger, LoggerFile)
        self.assertEqual(logger.logger_name, 'main')
    
    @override_settings(LOGGER_TYPE='FILE')
    def test_get_default_logger_case_insensitive_setting(self):
        """Test que get_default_logger gère la casse des settings"""
        logger = LoggerFactory.get_default_logger()
        
        self.assertIsInstance(logger, LoggerFile)
    
    def test_get_default_logger_custom_name(self):
        """Test de get_default_logger avec nom personnalisé"""
        with override_settings(LOGGER_TYPE='memory'):
            logger = LoggerFactory.get_default_logger('custom_default')
            
            self.assertIsInstance(logger, MemoryLogger)
            self.assertEqual(logger.logger_name, 'custom_default')
    
    @patch('main.utils.logger.LoggerFactory.settings')
    def test_get_default_logger_missing_setting(self, mock_settings):
        """Test de get_default_logger quand LOGGER_TYPE n'est pas défini"""
        # Simuler l'absence de LOGGER_TYPE dans settings
        mock_settings.LOGGER_TYPE = None
        
        with self.assertRaises(AttributeError):
            LoggerFactory.get_default_logger()
    
    def test_logger_interface_compliance(self):
        """Test que tous les loggers créés implémentent correctement l'interface ILogger"""
        loggers = [
            LoggerFactory.create_logger('test1', 'file'),
            LoggerFactory.create_logger('test2', 'memory')
        ]
        
        required_methods = ['debug', 'info', 'warning', 'error', 'critical', 'exception']
        
        for logger in loggers:
            self.assertIsInstance(logger, ILogger)
            
            for method_name in required_methods:
                self.assertTrue(hasattr(logger, method_name), 
                              f"Logger {type(logger).__name__} manque la méthode {method_name}")
                self.assertTrue(callable(getattr(logger, method_name)),
                              f"La méthode {method_name} de {type(logger).__name__} n'est pas callable")
    
    
    
    def test_logger_functionality_memory(self):
        """Test de fonctionnalité basique du MemoryLogger créé par la factory"""
        logger = LoggerFactory.create_logger('test_mem', 'memory')
        
        # Test des fonctionnalités spécifiques au MemoryLogger
        logger.info("Test message 1")
        logger.error("Test message 2")
        logger.debug("Test message 3")
        
        # Vérifier que les logs sont capturés
        all_logs = logger.get_logs()
        self.assertEqual(len(all_logs), 3)
        
        error_logs = logger.get_logs('ERROR')
        self.assertEqual(len(error_logs), 1)
        self.assertEqual(error_logs[0]['message'], "Test message 2")
        
        # Test du comptage
        self.assertEqual(logger.count_logs(), 3)
        self.assertEqual(logger.count_logs('INFO'), 1)
        
        # Test du nettoyage
        logger.clear_logs()
        self.assertEqual(logger.count_logs(), 0)
    
    def test_factory_thread_safety(self):
        """Test basique de thread safety (création simultanée de loggers)"""
        import threading
        import time
        
        created_loggers = []
        errors = []
        
        def create_logger_thread(thread_id):
            try:
                for i in range(10):
                    logger = LoggerFactory.create_logger(f'thread_{thread_id}_logger_{i}', 'memory')
                    created_loggers.append(logger)
                    time.sleep(0.001)  # Petite pause pour simuler le traitement
            except Exception as e:
                errors.append(f"Thread {thread_id}: {e}")
        
        # Créer plusieurs threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_logger_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Attendre que tous les threads terminent
        for thread in threads:
            thread.join()
        
        # Vérifier qu'il n'y a pas eu d'erreurs
        self.assertEqual(len(errors), 0, f"Erreurs de thread safety: {errors}")
        self.assertEqual(len(created_loggers), 50)  # 5 threads × 10 loggers
        
        # Vérifier que tous les loggers sont valides
        for logger in created_loggers:
            self.assertIsInstance(logger, MemoryLogger)
            self.assertIsNotNone(logger.logger_name)
    
    def test_factory_performance(self):
        """Test de performance basique de la factory"""
        import time
        
        start_time = time.time()
        
        # Créer beaucoup de loggers
        for i in range(100):
            LoggerFactory.create_logger(f'perf_test_{i}', 'memory')
        
        creation_time = time.time() - start_time
        
        # Vérifier que la création n'est pas trop lente
        # Seuil arbitraire qui peut être ajusté selon les besoins
        self.assertLess(creation_time, 1.0, "Factory performance too slow")
    
    def test_logger_isolation(self):
        """Test que les loggers créés sont bien isolés les uns des autres"""
        logger1 = LoggerFactory.create_logger('isolated1', 'memory')
        logger2 = LoggerFactory.create_logger('isolated2', 'memory')
        
        # Ajouter des logs différents
        logger1.info("Message from logger1")
        logger2.error("Message from logger2")
        
        # Vérifier l'isolation
        logs1 = logger1.get_logs()
        logs2 = logger2.get_logs()
        
        self.assertEqual(len(logs1), 1)
        self.assertEqual(len(logs2), 1)
        
        self.assertEqual(logs1[0]['message'], "Message from logger1")
        self.assertEqual(logs1[0]['level'], 'INFO')
        
        self.assertEqual(logs2[0]['message'], "Message from logger2")
        self.assertEqual(logs2[0]['level'], 'ERROR')
        
        # Nettoyer un logger ne doit pas affecter l'autre
        logger1.clear_logs()
        
        self.assertEqual(len(logger1.get_logs()), 0)
        self.assertEqual(len(logger2.get_logs()), 1)
    
    @override_settings(LOGGER_TYPE='invalid_type')
    def test_get_default_logger_invalid_setting(self):
        """Test de get_default_logger avec un type invalide dans settings"""
        with self.assertRaises(ValueError) as context:
            LoggerFactory.get_default_logger()
        
        self.assertIn('Type de logger non supporté: invalid_type', str(context.exception))


class LoggerFactoryIntegrationTestCase(TestCase):
    """Tests d'intégration pour LoggerFactory avec Django"""
    
    @override_settings(
        LOGGER_TYPE='memory',
        DEBUG=True
    )
    def test_factory_with_django_settings_memory(self):
        """Test d'intégration avec settings Django pour MemoryLogger"""
        logger = LoggerFactory.get_default_logger('django_integration')
        
        self.assertIsInstance(logger, MemoryLogger)
        self.assertEqual(logger.logger_name, 'django_integration')
        
        # Test de fonctionnement avec Django
        logger.info("Integration test with Django settings")
        logs = logger.get_logs()
        
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['message'], "Integration test with Django settings")
    
    @override_settings(
        LOGGER_TYPE='file',
        DEBUG=False
    )
    def test_factory_with_django_settings_file(self):
        """Test d'intégration avec settings Django pour LoggerFile"""
        logger = LoggerFactory.get_default_logger('django_file_integration')
        
        self.assertIsInstance(logger, LoggerFile)
        self.assertEqual(logger.logger_name, 'django_file_integration')
        
        # Test de fonctionnement (ne peut pas vérifier les logs facilement avec LoggerFile)
        try:
            logger.info("Integration test with Django file logger")
        except Exception as e:
            self.fail(f"LoggerFile integration failed: {e}")
    
    def test_factory_consistent_behavior(self):
        """Test que la factory produit un comportement cohérent"""
        # Créer plusieurs fois le même type de logger
        loggers = []
        for _ in range(5):
            logger = LoggerFactory.create_logger('consistent_test', 'memory')
            loggers.append(logger)
        
        # Tous doivent être du même type
        for logger in loggers:
            self.assertIsInstance(logger, MemoryLogger)
            self.assertEqual(logger.logger_name, 'consistent_test')
        
        # Mais ce doivent être des instances différentes
        logger_ids = [id(logger) for logger in loggers]
        self.assertEqual(len(set(logger_ids)), 5, "Loggers should be different instances")
    
    def test_factory_with_real_django_logging(self):
        """Test que LoggerFile interagit correctement avec le système de logging Django"""
        logger = LoggerFactory.create_logger('django_logging_test', 'file')
        
        # Vérifier que le logger Django sous-jacent existe
        self.assertIsNotNone(logger.logger)
        self.assertEqual(logger.logger.name, 'django_logging_test')
        
        # Test avec le handler de logging Django (si configuré)
        with patch('logging.getLogger') as mock_get_logger:
            mock_django_logger = MagicMock()
            mock_get_logger.return_value = mock_django_logger
            
            test_logger = LoggerFactory.create_logger('mock_test', 'file')
            test_logger.info("Test message")
            
            mock_get_logger.assert_called_with('mock_test')
            mock_django_logger.info.assert_called_with("Test message")


# Export des classes de test pour l'import dans tests.py
__all__ = ['LoggerFactoryTestCase', 'LoggerFactoryIntegrationTestCase']