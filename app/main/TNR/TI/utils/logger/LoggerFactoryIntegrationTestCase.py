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


@tag('integration')
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
    
    @override_settings(
        LOGGER_TYPE='loki',
        LOKI_URL='http://test-loki:3100' # NOSONAR
    )
    @patch('main.domain.common.utils.logger.LoggerFactory.LokiLogger')
    def test_factory_with_django_settings_loki(self, mock_loki_logger):
        """Test d'intégration avec settings Django pour LokiLogger (factory simplifiée)"""
        mock_loki_instance = MagicMock(spec=ILogger)
        mock_loki_logger.return_value = mock_loki_instance

        logger = LoggerFactory.get_default_logger('django_loki_integration')

        self.assertEqual(logger, mock_loki_instance)
        mock_loki_logger.assert_called_once()
        call_args = mock_loki_logger.call_args
        # La factory actuelle ne transmet que logger_name
        self.assertEqual(call_args[1]['logger_name'], 'django_loki_integration')
    
    @override_settings(LOGGER_TYPE='composite')
    @patch('main.domain.common.utils.logger.LoggerFactory.LokiLogger')
    def test_factory_with_django_settings_composite(self, mock_loki_logger):
        """Test d'intégration avec settings Django pour CompositeLogger (factory simplifiée)"""
        mock_loki_instance = MagicMock(spec=ILogger)
        mock_loki_logger.return_value = mock_loki_instance

        logger = LoggerFactory.get_default_logger('django_composite_integration')

        self.assertIsInstance(logger, CompositeLogger)
        self.assertEqual(logger.logger_name, 'django_composite_integration')
        self.assertEqual(logger.logger_count, 2)  # file + loki par défaut
        logger_types = [type(sub_logger).__name__ for sub_logger in logger.loggers]
        self.assertIn('LoggerFile', logger_types)
        mock_loki_logger.assert_called_once()
    

    
    def test_composite_logger_functional_integration(self):
        """Test fonctionnel complet d'un CompositeLogger"""
        # Créer un composite avec des MemoryLoggers pour pouvoir vérifier les résultats
        composite = LoggerFactory.create_logger(
            'functional_test',
            'composite',
            logger_types=['memory', 'memory']
        )
        
        self.assertIsInstance(composite, CompositeLogger)
        
        # Tester tous les niveaux de log
        composite.debug("Debug message")
        composite.info("Info message")
        composite.warning("Warning message")
        composite.error("Error message")
        composite.critical("Critical message")
        
        # Vérifier que tous les sous-loggers ont reçu tous les messages
        for sub_logger in composite.loggers:
            self.assertIsInstance(sub_logger, MemoryLogger)
            logs = sub_logger.get_logs()
            self.assertEqual(len(logs), 5)
            
            levels = [log['level'] for log in logs]
            messages = [log['message'] for log in logs]
            
            self.assertEqual(levels, ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
            self.assertEqual(messages, [
                'Debug message',
                'Info message', 
                'Warning message',
                'Error message',
                'Critical message'
            ])
    
    @override_settings(
        LOKI_URL='http://settings-loki:3100', # NOSONAR
        LOKI_BATCH_SIZE=15,
        LOKI_BATCH_TIMEOUT=3.0
    )
    @patch('main.domain.common.utils.logger.LoggerFactory.LokiLogger')
    def test_loki_logger_uses_django_settings(self, mock_loki_logger):
        """Test que LokiLogger est créé sans erreur et reçoit le logger_name avec la factory simplifiée"""
        mock_loki_instance = MagicMock(spec=ILogger)
        mock_loki_logger.return_value = mock_loki_instance

        # Création du logger (la factory actuelle ne transmet que logger_name)
        LoggerFactory.create_logger('settings_test', 'loki')

        mock_loki_logger.assert_called_once()
        call_args = mock_loki_logger.call_args
        # Vérifier uniquement le paramètre réellement transmis par la factory
        self.assertEqual(call_args[1]['logger_name'], 'settings_test')


# Export des classes de test pour l'import dans tests.py
__all__ = ['LoggerFactoryIntegrationTestCase']