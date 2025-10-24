"""
Tests unitaires pour LoggerFactory.
Tests de la factory de création de loggers avec différents types et configurations.
"""

import logging
from django.test import TestCase, override_settings, tag
from django.conf import settings
from unittest.mock import patch, MagicMock

from main.domain.common.utils.logger.LoggerFactory import LoggerFactory
from main.domain.common.utils.logger.ILogger import ILogger
from main.domain.common.utils.logger.LoggerFile import LoggerFile
from main.domain.common.utils.logger.MemoryLogger import MemoryLogger
from main.domain.common.utils.logger.LokiLogger import LokiLogger
from main.domain.common.utils.logger.CompositeLogger import CompositeLogger


@tag('unitaire')
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
        self.assertIn("Types supportés: 'file', 'memory', 'loki', 'composite'", error_message)
    
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
    
    @patch('main.domain.common.utils.logger.LoggerFactory.Settings')
    def test_get_default_logger_missing_setting(self, mock_settings):
        """Test de get_default_logger quand LOGGER_TYPE n'est pas défini"""
        # Simuler l'absence de LOGGER_TYPE dans settings
        mock_settings.get.return_value = None
        
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
    
    @patch('main.domain.common.utils.logger.LoggerFactory.LokiLogger')
    def test_create_loki_logger(self, mock_loki_logger):
        """Test de création d'un LokiLogger"""
        mock_loki_instance = MagicMock(spec=ILogger)
        mock_loki_logger.return_value = mock_loki_instance

        instance = LoggerFactory.create_logger('test_loki', 'loki')

        self.assertIs(instance, mock_loki_instance)
        mock_loki_logger.assert_called_once()
        call_args = mock_loki_logger.call_args
        # Implémentation actuelle: seul logger_name est transmis
        self.assertEqual(call_args[1]['logger_name'], 'test_loki')
    
    @patch('main.domain.common.utils.logger.LoggerFactory.LokiLogger')
    def test_create_loki_logger_with_custom_params(self, mock_loki_logger):
        """Test de création d'un LokiLogger avec paramètres personnalisés"""
        mock_loki_instance = MagicMock(spec=ILogger)
        mock_loki_logger.return_value = mock_loki_instance

        custom_labels = {'service': 'test_service'}
        instance = LoggerFactory.create_logger(
            'test_loki_custom',
            'loki',
            loki_url='http://custom-loki:3100', # NOSONAR
            labels=custom_labels,
            batch_size=20,
            batch_timeout=10.0
        )

        self.assertIs(instance, mock_loki_instance)
        mock_loki_logger.assert_called_once()
        call_args = mock_loki_logger.call_args
        self.assertEqual(call_args[1]['logger_name'], 'test_loki_custom')
    
    def test_create_composite_logger(self):
        """Test de création d'un CompositeLogger"""
        logger = LoggerFactory.create_logger(
            'test_composite',
            'composite',
            logger_types=['memory', 'memory']  # Deux MemoryLoggers pour les tests
        )
        
        self.assertIsInstance(logger, CompositeLogger)
        self.assertEqual(logger.logger_name, 'test_composite')
        self.assertEqual(logger.logger_count, 2)
        
        # Vérifier que ce sont bien des MemoryLoggers
        for sub_logger in logger.loggers:
            self.assertIsInstance(sub_logger, MemoryLogger)
    
    @patch('main.domain.common.utils.logger.LoggerFactory.LokiLogger')
    def test_create_composite_logger_with_mixed_types(self, mock_loki_logger):
        """Test de création d'un CompositeLogger avec types mixtes"""
        mock_loki_instance = MagicMock(spec=ILogger)
        mock_loki_logger.return_value = mock_loki_instance

        logger = LoggerFactory.create_logger(
            'test_mixed_composite',
            'composite',
            logger_types=['memory', 'file', 'loki']
        )
        
        self.assertIsInstance(logger, CompositeLogger)
        self.assertEqual(logger.logger_name, 'test_mixed_composite')
        self.assertEqual(logger.logger_count, 3)
        
        # Vérifier les types des sous-loggers
        logger_types = [type(sub_logger).__name__ for sub_logger in logger.loggers]
        self.assertIn('MemoryLogger', logger_types)
        self.assertIn('LoggerFile', logger_types)
        # LokiLogger est mocké
        mock_loki_logger.assert_called_once()
    
    @patch('main.domain.common.utils.logger.LoggerFactory.LokiLogger')
    def test_create_composite_logger_default_types(self, mock_loki_logger):
        """Test de création d'un CompositeLogger avec types par défaut"""
        mock_loki_instance = MagicMock(spec=ILogger)
        mock_loki_logger.return_value = mock_loki_instance

        logger = LoggerFactory.create_logger('test_default_composite', 'composite')

        self.assertIsInstance(logger, CompositeLogger)
        # Par défaut: ['file', 'loki'] => 2 sous-loggers
        self.assertEqual(logger.logger_count, 2)
        mock_loki_logger.assert_called_once()
    

    @patch('main.domain.common.utils.logger.LoggerFactory.LokiLogger')
    def test_create_composite_logger_with_failing_sublogger(self, mock_loki_logger):
        """Test de création d'un CompositeLogger quand un sous-logger échoue"""
        # Faire échouer la création du LokiLogger
        mock_loki_logger.side_effect = Exception("LokiLogger creation failed")

        logger = LoggerFactory.create_logger(
            'test_failing_sublogger',
            'composite',
            logger_types=['memory', 'loki', 'file']
        )

        self.assertIsInstance(logger, CompositeLogger)
        # Seuls memory et file devraient être créés (loki a échoué)
        self.assertEqual(logger.logger_count, 2)

        logger_types = [type(sub_logger).__name__ for sub_logger in logger.loggers]
        self.assertIn('MemoryLogger', logger_types)
        self.assertIn('LoggerFile', logger_types)
    
    @patch('main.domain.common.utils.logger.LoggerFactory.LokiLogger')
    def test_loki_logger_case_insensitive(self, mock_loki_logger):
        """Test que le type loki est insensible à la casse"""
        mock_loki_instance = MagicMock(spec=ILogger)
        mock_loki_logger.return_value = mock_loki_instance
        logger_upper = LoggerFactory.create_logger('test', 'LOKI') # NOSONAR
        logger_mixed = LoggerFactory.create_logger('test', 'Loki') # NOSONAR
        self.assertIs(logger_upper, mock_loki_instance)
        self.assertIs(logger_mixed, mock_loki_instance)
        self.assertEqual(mock_loki_logger.call_count, 2)
            
    
    def test_composite_logger_case_insensitive(self):
        """Test que le type composite est insensible à la casse"""
        logger_upper = LoggerFactory.create_logger('test', 'COMPOSITE', logger_types=['memory'])
        logger_mixed = LoggerFactory.create_logger('test', 'Composite', logger_types=['memory'])
        
        self.assertIsInstance(logger_upper, CompositeLogger)
        self.assertIsInstance(logger_mixed, CompositeLogger)


# Export des classes de test pour l'import dans tests.py
__all__ = ['LoggerFactoryTestCase']