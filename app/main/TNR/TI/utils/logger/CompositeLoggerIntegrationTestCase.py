"""
Tests unitaires pour CompositeLogger.
Tests de l'implémentation du logger composite qui combine plusieurs loggers.
"""

from unittest.mock import MagicMock, patch
from django.test import TestCase, tag
from unittest import TestCase as UnitTestCase

from main.domain.common.utils.logger.CompositeLogger import CompositeLogger
from main.domain.common.utils.logger.ILogger import ILogger
from main.domain.common.utils.logger.MemoryLogger import MemoryLogger
from main.domain.common.utils.logger.LoggerFile import LoggerFile



@tag('integration')
class CompositeLoggerIntegrationTestCase(TestCase):
    """Tests d'intégration pour CompositeLogger avec Django"""
    
    def test_composite_with_logger_factory(self):
        """Test d'intégration avec LoggerFactory"""
        from main.domain.common.utils.logger.LoggerFactory import LoggerFactory
        
        # Créer un logger composite via la factory
        composite = LoggerFactory.create_logger(
            'factory_composite',
            'composite',
            logger_types=['memory', 'memory']  # Deux MemoryLoggers pour les tests
        )
        
        self.assertIsInstance(composite, CompositeLogger)
        self.assertEqual(composite.logger_name, 'factory_composite')
        self.assertEqual(composite.logger_count, 2)
        
        # Tester le fonctionnement
        composite.info("Factory integration test")
        
        # Tous les sous-loggers devraient avoir reçu le message
        for logger in composite.loggers:
            self.assertIsInstance(logger, MemoryLogger)
            logs = logger.get_logs()
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]['message'], "Factory integration test")
    
   

# Export des classes de test
__all__ = ['CompositeLoggerIntegrationTestCase']