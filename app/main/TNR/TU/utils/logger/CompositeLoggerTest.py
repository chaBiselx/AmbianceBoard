"""
Tests unitaires pour CompositeLogger.
Tests de l'implémentation du logger composite qui combine plusieurs loggers.
"""

from unittest.mock import MagicMock, patch
from django.test import TestCase
from unittest import TestCase as UnitTestCase

from main.domain.common.utils.logger.CompositeLogger import CompositeLogger
from main.domain.common.utils.logger.ILogger import ILogger
from main.domain.common.utils.logger.MemoryLogger import MemoryLogger
from main.domain.common.utils.logger.LoggerFile import LoggerFile


class CompositeLoggerTestCase(UnitTestCase):
    """Tests unitaires pour CompositeLogger"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        # Créer des loggers de test
        self.memory_logger1 = MemoryLogger('test_memory1')
        self.memory_logger2 = MemoryLogger('test_memory2')
        self.mock_logger = MagicMock(spec=ILogger)
        
    def tearDown(self):
        """Nettoyage après chaque test"""
        pass
    
    def test_composite_logger_initialization(self):
        """Test d'initialisation du CompositeLogger"""
        loggers = [self.memory_logger1, self.memory_logger2]
        composite = CompositeLogger('test_composite', loggers)
        
        self.assertIsInstance(composite, ILogger)
        self.assertEqual(composite.logger_name, 'test_composite')
        self.assertEqual(composite.logger_count, 2)
        self.assertEqual(len(composite.loggers), 2)
    
    def test_composite_logger_default_initialization(self):
        """Test d'initialisation avec les paramètres par défaut"""
        composite = CompositeLogger()
        
        self.assertEqual(composite.logger_name, 'composite')
        self.assertEqual(composite.logger_count, 0)
        self.assertEqual(len(composite.loggers), 0)
    
    def test_composite_logger_empty_name_raises_error(self):
        """Test qu'un nom vide lève une exception"""
        with self.assertRaises(ValueError) as context:
            CompositeLogger(logger_name='')
        
        self.assertIn("Le nom du logger ne peut pas être vide", str(context.exception))
    
    def test_add_logger(self):
        """Test d'ajout de logger"""
        composite = CompositeLogger('test_add')
        
        self.assertEqual(composite.logger_count, 0)
        
        composite.add_logger(self.memory_logger1)
        self.assertEqual(composite.logger_count, 1)
        
        composite.add_logger(self.memory_logger2)
        self.assertEqual(composite.logger_count, 2)
        
        # Ajouter le même logger ne devrait pas l'ajouter deux fois
        composite.add_logger(self.memory_logger1)
        self.assertEqual(composite.logger_count, 2)
    
    def test_remove_logger(self):
        """Test de suppression de logger"""
        loggers = [self.memory_logger1, self.memory_logger2]
        composite = CompositeLogger('test_remove', loggers)
        
        self.assertEqual(composite.logger_count, 2)
        
        composite.remove_logger(self.memory_logger1)
        self.assertEqual(composite.logger_count, 1)
        self.assertNotIn(self.memory_logger1, composite.loggers)
        
        # Supprimer un logger qui n'existe pas ne devrait pas lever d'erreur
        composite.remove_logger(self.memory_logger1)
        self.assertEqual(composite.logger_count, 1)
    
    def test_debug_message_delegation(self):
        """Test de délégation des messages DEBUG"""
        loggers = [self.memory_logger1, self.memory_logger2, self.mock_logger]
        composite = CompositeLogger('test_debug', loggers)
        
        msg_debug = "Debug message test"
        composite.debug(msg_debug)
        
        # Vérifier que les MemoryLoggers ont reçu le message
        logs1 = self.memory_logger1.get_logs()
        logs2 = self.memory_logger2.get_logs()
        
        self.assertEqual(len(logs1), 1)
        self.assertEqual(len(logs2), 1)
        self.assertEqual(logs1[0]['message'], msg_debug)
        self.assertEqual(logs1[0]['level'], 'DEBUG')
        self.assertEqual(logs2[0]['message'], msg_debug)
        self.assertEqual(logs2[0]['level'], 'DEBUG')
        
        # Vérifier que le mock logger a été appelé
        self.mock_logger.debug.assert_called_once_with(msg_debug)
    
    def test_info_message_delegation(self):
        """Test de délégation des messages INFO"""
        loggers = [self.memory_logger1, self.memory_logger2]
        composite = CompositeLogger('test_info', loggers)
        
        composite.info("Info message test")
        
        for logger in [self.memory_logger1, self.memory_logger2]:
            logs = logger.get_logs()
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]['message'], "Info message test")
            self.assertEqual(logs[0]['level'], 'INFO')
    
    def test_warning_message_delegation(self):
        """Test de délégation des messages WARNING"""
        loggers = [self.memory_logger1, self.memory_logger2]
        composite = CompositeLogger('test_warning', loggers)
        
        composite.warning("Warning message test")
        
        for logger in [self.memory_logger1, self.memory_logger2]:
            logs = logger.get_logs()
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]['message'], "Warning message test")
            self.assertEqual(logs[0]['level'], 'WARNING')
    
    def test_error_message_delegation(self):
        """Test de délégation des messages ERROR"""
        loggers = [self.memory_logger1, self.memory_logger2]
        composite = CompositeLogger('test_error', loggers)
        
        composite.error("Error message test")
        
        for logger in [self.memory_logger1, self.memory_logger2]:
            logs = logger.get_logs()
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]['message'], "Error message test")
            self.assertEqual(logs[0]['level'], 'ERROR')
    
    def test_critical_message_delegation(self):
        """Test de délégation des messages CRITICAL"""
        loggers = [self.memory_logger1, self.memory_logger2]
        composite = CompositeLogger('test_critical', loggers)
        
        composite.critical("Critical message test")
        
        for logger in [self.memory_logger1, self.memory_logger2]:
            logs = logger.get_logs()
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]['message'], "Critical message test")
            self.assertEqual(logs[0]['level'], 'CRITICAL')
    
    def test_exception_message_delegation(self):
        """Test de délégation des messages d'exception"""
        loggers = [self.memory_logger1, self.memory_logger2]
        composite = CompositeLogger('test_exception', loggers)
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            composite.exception("Exception occurred")
        
        for logger in [self.memory_logger1, self.memory_logger2]:
            logs = logger.get_logs()
            self.assertEqual(len(logs), 1)
            self.assertIn("Exception occurred", logs[0]['message'])
            self.assertEqual(logs[0]['level'], 'ERROR')
    
    def test_message_with_arguments(self):
        """Test de délégation avec arguments de formatage"""
        loggers = [self.memory_logger1, self.memory_logger2]
        composite = CompositeLogger('test_args', loggers)
        
        composite.info("User %s has %d points", "john", 100)
        
        for logger in [self.memory_logger1, self.memory_logger2]:
            logs = logger.get_logs()
            self.assertEqual(len(logs), 1)
            # MemoryLogger ne formate pas automatiquement, donc on vérifie les args
            self.assertEqual(logs[0]['message'], "User %s has %d points")
            self.assertEqual(logs[0]['args'], ("john", 100))
    
    def test_message_with_kwargs(self):
        """Test de délégation avec arguments nommés"""
        loggers = [self.memory_logger1, self.memory_logger2]
        composite = CompositeLogger('test_kwargs', loggers)
        
        composite.info("Test message", extra={'user_id': 123})
        
        for logger in [self.memory_logger1, self.memory_logger2]:
            logs = logger.get_logs()
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]['message'], "Test message")
            self.assertEqual(logs[0]['kwargs'], {'extra': {'user_id': 123}})
    
    def test_error_handling_in_delegation(self):
        """Test de la gestion d'erreur lors de la délégation"""
        # Créer un logger qui lève une exception
        failing_logger = MagicMock(spec=ILogger)
        failing_logger.info.side_effect = Exception("Logger error")
        
        loggers = [self.memory_logger1, failing_logger, self.memory_logger2]
        composite = CompositeLogger('test_error_handling', loggers)
        
        log_message = "Test message with failing logger"
        # Cela ne devrait pas lever d'exception malgré l'erreur du failing_logger
        composite.info(log_message)
        
        # Vérifier que les autres loggers ont fonctionné
        logs1 = self.memory_logger1.get_logs()
        logs2 = self.memory_logger2.get_logs()
        
        self.assertEqual(len(logs1), 1)
        self.assertEqual(len(logs2), 1)
        self.assertEqual(logs1[0]['message'], log_message)
        self.assertEqual(logs2[0]['message'], log_message)
        
        # Vérifier que le failing_logger a été appelé mais a échoué
        failing_logger.info.assert_called_once()
    
    def test_flush_method(self):
        """Test de la méthode flush"""
        # Créer des loggers avec méthode flush
        logger_with_flush = MagicMock(spec=ILogger)
        logger_with_flush.flush = MagicMock()
        
        logger_without_flush = MagicMock(spec=ILogger)
        # Ce logger n'a pas de méthode flush
        
        loggers = [self.memory_logger1, logger_with_flush, logger_without_flush]
        composite = CompositeLogger('test_flush', loggers)
        
        # Appeler flush ne devrait pas lever d'exception
        composite.flush()
        
        # Vérifier que flush a été appelé sur le logger qui l'a
        logger_with_flush.flush.assert_called_once()
    
    def test_shutdown_method(self):
        """Test de la méthode shutdown"""
        # Créer des loggers avec méthode shutdown
        logger_with_shutdown = MagicMock(spec=ILogger)
        logger_with_shutdown.shutdown = MagicMock()
        
        logger_without_shutdown = MagicMock(spec=ILogger)
        # Ce logger n'a pas de méthode shutdown
        
        loggers = [self.memory_logger1, logger_with_shutdown, logger_without_shutdown]
        composite = CompositeLogger('test_shutdown', loggers)
        
        # Appeler shutdown ne devrait pas lever d'exception
        composite.shutdown()
        
        # Vérifier que shutdown a été appelé sur le logger qui l'a
        logger_with_shutdown.shutdown.assert_called_once()
    
    def test_properties(self):
        """Test des propriétés du CompositeLogger"""
        loggers = [self.memory_logger1, self.memory_logger2]
        composite = CompositeLogger('test_properties', loggers)
        
        self.assertEqual(composite.logger_name, 'test_properties')
        self.assertEqual(composite.logger_count, 2)
        
        # Vérifier que loggers retourne une copie
        returned_loggers = composite.loggers
        self.assertEqual(len(returned_loggers), 2)
        self.assertIsNot(returned_loggers, composite._loggers)  # Doit être une copie
    
    def test_string_representations(self):
        """Test des représentations string du CompositeLogger"""
        loggers = [self.memory_logger1, self.memory_logger2]
        composite = CompositeLogger('test_repr', loggers)
        
        str_repr = str(composite)
        repr_repr = repr(composite)
        
        self.assertIn('CompositeLogger', str_repr)
        self.assertIn('test_repr', str_repr)
        self.assertIn('MemoryLogger', str_repr)
        
        self.assertIn('CompositeLogger', repr_repr)
        self.assertIn('test_repr', repr_repr)
        self.assertIn('2', repr_repr)  # logger_count
    
    def test_empty_composite_logger(self):
        """Test d'un CompositeLogger sans loggers"""
        composite = CompositeLogger('empty_test')
        
        # Toutes les méthodes de logging devraient fonctionner sans erreur
        composite.debug("Debug message")
        composite.info("Info message")
        composite.warning("Warning message")
        composite.error("Error message")
        composite.critical("Critical message")
        composite.exception("Exception message")
        
        # flush et shutdown devraient aussi fonctionner
        composite.flush()
        composite.shutdown()
        
        # Aucune exception ne devrait être levée
        self.assertEqual(composite.logger_count, 0)
    
    def test_composite_logger_with_different_logger_types(self):
        """Test avec différents types de loggers"""
        from main.domain.common.utils.logger.LoggerFile import LoggerFile
        
        file_logger = LoggerFile('test_file')
        memory_logger = MemoryLogger('test_memory')
        mock_logger = MagicMock(spec=ILogger)
        
        loggers = [file_logger, memory_logger, mock_logger]
        composite = CompositeLogger('mixed_types', loggers)
        
        message = "Test message for mixed types"
        composite.info(message)
        
        # Vérifier que tous ont été appelés
        memory_logs = memory_logger.get_logs()
        self.assertEqual(len(memory_logs), 1)
        self.assertEqual(memory_logs[0]['message'], message)
        
        mock_logger.info.assert_called_once_with(message)
        
        # Le LoggerFile devrait avoir traité le message (pas d'exception)
        self.assertEqual(composite.logger_count, 3)
    
    def test_isolated_logger_state(self):
        """Test que l'état des loggers reste isolé"""
        logger1 = MemoryLogger('isolated1')
        logger2 = MemoryLogger('isolated2')
        
        composite = CompositeLogger('isolation_test', [logger1, logger2])
        
        # Ajouter des messages différents directement aux loggers
        logger1.debug("Direct message to logger1")
        logger2.error("Direct message to logger2")
        
        # Ajouter un message via le composite
        message = "Composite message"
        composite.info(message)
        
        # Vérifier l'isolation
        logs1 = logger1.get_logs()
        logs2 = logger2.get_logs()
        
        self.assertEqual(len(logs1), 2)  # direct + composite
        self.assertEqual(len(logs2), 2)  # direct + composite
        
        # Vérifier les messages spécifiques
        self.assertEqual(logs1[0]['message'], "Direct message to logger1")
        self.assertEqual(logs1[0]['level'], 'DEBUG')
        self.assertEqual(logs1[1]['message'], message)
        self.assertEqual(logs1[1]['level'], 'INFO')
        
        self.assertEqual(logs2[0]['message'], "Direct message to logger2")
        self.assertEqual(logs2[0]['level'], 'ERROR')
        self.assertEqual(logs2[1]['message'], message)
        self.assertEqual(logs2[1]['level'], 'INFO')


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
__all__ = ['CompositeLoggerTestCase', 'CompositeLoggerIntegrationTestCase']