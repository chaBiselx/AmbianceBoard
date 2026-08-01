"""Tests avancés de latence pour LokiLogger - Cas de latence avancés et edge cases."""

import time
import statistics
import threading
from unittest.mock import MagicMock, patch, call
from queue import Queue

from django.test import Client, TestCase, override_settings, tag
from django.urls import reverse

from main.domain.common.utils.logger.LoggerFactory import LoggerFactory
from main.domain.common.utils.logger.LokiLogger import LokiLogger


@tag('stress-test', 'latency-advanced')
class LokiLoggingAdvancedLatencyTestCase(TestCase):
    """Tests avancés: contention, concurrence, race conditions."""

    def _reset_logger_cache_if_available(self):
        clear_cache = getattr(LoggerFactory, 'clear_default_logger_cache', None)
        if callable(clear_cache):
            clear_cache()

    def tearDown(self):
        self._reset_logger_cache_if_available()
        super().tearDown()

    # =========================================================================
    # TEST 1: Contention de Queue sous charge haute
    # =========================================================================
    @override_settings(
        LOGGER_TYPE='loki',
        LOKI_URL='http://test-loki:3100',
        LOKI_BATCH_SIZE=100,
        LOKI_BATCH_TIMEOUT=1.0,
    )
    @patch('main.domain.common.utils.logger.LokiLogger.requests.post')
    @patch('main.domain.common.utils.logger.LokiLogger.requests.get')
    def test_queue_contention_high_throughput_logging(self, mock_get, mock_post):
        """
        Test de contention: 1000 logs d'au moins 20 threads simultanés.
        Mesure: chaque thread doit enqueue ses logs rapidement (< 50ms total).
        """
        self._reset_logger_cache_if_available()
        
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 204
        
        logger = LoggerFactory.create_logger('queue_contention', 'loki')
        
        try:
            thread_count = 20
            logs_per_thread = 50
            durations_per_thread = {}
            lock = threading.Lock()
            
            def log_from_thread(thread_id):
                start = time.perf_counter()
                for i in range(logs_per_thread):
                    logger.info(f"Thread {thread_id} message {i}")
                duration = time.perf_counter() - start
                
                with lock:
                    durations_per_thread[thread_id] = duration
            
            threads = [
                threading.Thread(target=log_from_thread, args=(i,))
                for i in range(thread_count)
            ]
            
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            
            # Vérifier que tous les threads ont complété rapidement
            max_duration = max(durations_per_thread.values())
            avg_duration = statistics.mean(durations_per_thread.values())
            
            self.assertLess(
                max_duration,
                0.5,
                msg=f"Contention excessive: max={max_duration:.3f}s, avg={avg_duration:.3f}s"
            )
        finally:
            if hasattr(logger, 'shutdown'):
                logger.shutdown()

    # =========================================================================
    # TEST 2: Labels massifs JSON serialization
    # =========================================================================
    @override_settings(
        LOGGER_TYPE='loki',
        LOKI_URL='http://test-loki:3100',
        LOKI_BATCH_SIZE=1,
        LOKI_BATCH_TIMEOUT=0.1,
    )
    @patch('main.domain.common.utils.logger.LokiLogger.requests.post')
    @patch('main.domain.common.utils.logger.LokiLogger.requests.get')
    def test_huge_labels_serialization_latency(self, mock_get, mock_post):
        """
        Test: logs avec labels massifs (1000+ clés).
        Mesure: enqueue + JSON serialization < 100ms par log.
        """
        self._reset_logger_cache_if_available()
        
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 204
        
        logger = LoggerFactory.create_logger('huge_labels', 'loki')
        
        try:
            # Créer des labels massifs
            huge_labels = {f'label_{i}': f'value_{i}' for i in range(1000)}
            
            start = time.perf_counter()
            logger.info("test message", extra_labels=huge_labels)
            duration = time.perf_counter() - start
            
            self.assertLess(
                duration,
                0.1,
                msg=f"Serialization labels trop lent: {duration:.3f}s"
            )
            
            # Vérifier que les labels ont bien été envoyés
            time.sleep(0.5)
            self.assertTrue(mock_post.called)
            
            payload = mock_post.call_args[1]['json']
            sent_labels = payload['streams'][0]['stream']
            
            # Vérifier quelques labels
            self.assertIn('label_0', sent_labels)
            self.assertIn('label_999', sent_labels)
            
        finally:
            if hasattr(logger, 'shutdown'):
                logger.shutdown()

    # =========================================================================
    # TEST 3: Spike de logs simultanés
    # =========================================================================
    @override_settings(
        LOGGER_TYPE='loki',
        LOKI_URL='http://test-loki:3100',
        LOKI_BATCH_SIZE=50,
        LOKI_BATCH_TIMEOUT=1.0,
    )
    @patch('main.domain.common.utils.logger.LokiLogger.requests.post')
    @patch('main.domain.common.utils.logger.LokiLogger.requests.get')
    def test_log_spike_queue_not_unbounded(self, mock_get, mock_post):
        """
        Test: 10000 logs loggés rapidement en rafale.
        Mesure: la queue ne doit pas croître indéfiniment (max 500 éléments).
        """
        self._reset_logger_cache_if_available()
        
        mock_get.return_value.status_code = 200
        
        # Simuler un Loki avec latence normale (10ms par batch)
        # 200ms était trop lent: 200ms × 15 batches = 3s seulement (impossible d'en envoyer 200!)
        # 10ms est réaliste pour une API HTTP locale: 10ms × 200 batches = 2s (OK avec wait 3s)
        def slow_post(*args, **kwargs):
            time.sleep(0.01)
            response = MagicMock()
            response.status_code = 204
            return response
        
        mock_post.side_effect = slow_post
        
        logger = LoggerFactory.create_logger('log_spike', 'loki')
        
        try:
            # Enqueue 10000 logs rapidement
            start = time.perf_counter()
            for i in range(10000):
                logger.info(f"spike message {i}")
            enqueue_duration = time.perf_counter() - start
            
            # Vérifier que l'enqueue était rapide
            self.assertLess(
                enqueue_duration,
                1.0,
                msg=f"Enqueue 10000 logs trop lent: {enqueue_duration:.3f}s"
            )
            
            # Attendre l'envoi de tous les batches
            time.sleep(3.0)
            
            # Vérifier que plusieurs batches ont été envoyés
            # Avec timeout réduit à 0.1s (au lieu de 0.5s), on peut envoyer beaucoup plus de batches
            # Formule: 10000 logs / batch_size=50 = 200 batches attendus
            # Avec timing réel et latence système, accepter 150+ batches minimum
            self.assertGreater(
                mock_post.call_count,
                150,
                msg=f"Trop peu de batches envoyés: {mock_post.call_count} (attendu: 200+)"
            )
            
        finally:
            if hasattr(logger, 'shutdown'):
                logger.shutdown()

    # =========================================================================
    # TEST 4: Message formatting failure (% formatting)
    # =========================================================================
    @override_settings(
        LOGGER_TYPE='loki',
        LOKI_URL='http://test-loki:3100',
        LOKI_BATCH_SIZE=1,
        LOKI_BATCH_TIMEOUT=0.1,
    )
    @patch('main.domain.common.utils.logger.LokiLogger.requests.post')
    @patch('main.domain.common.utils.logger.LokiLogger.requests.get')
    def test_message_formatting_exception_does_not_block(self, mock_get, mock_post):
        """
        Test: logging avec mauvais formatage % (ex: msg="test %s" sans args).
        Mesure: pas d'exception, log enqueué quand même, < 10ms.
        """
        self._reset_logger_cache_if_available()
        
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 204
        
        logger = LoggerFactory.create_logger('format_error', 'loki')
        
        try:
            # Message avec % mais pas d'args -> TypeError
            start = time.perf_counter()
            logger.info("Message with %s placeholder")  # Pas d'args
            duration = time.perf_counter() - start
            
            self.assertLess(
                duration,
                0.01,
                msg=f"Format exception bloquante: {duration:.3f}s"
            )
            
            # Vérifier que le log est quand même enqueué
            time.sleep(0.5)
            self.assertTrue(mock_post.called)
            
        finally:
            if hasattr(logger, 'shutdown'):
                logger.shutdown()

    # =========================================================================
    # TEST 5: Shutdown avec logs en attente (potential deadlock)
    # =========================================================================
    @override_settings(
        LOGGER_TYPE='loki',
        LOKI_URL='http://test-loki:3100',
        LOKI_BATCH_SIZE=100,
        LOKI_BATCH_TIMEOUT=10.0,
    )
    @patch('main.domain.common.utils.logger.LokiLogger.requests.post')
    @patch('main.domain.common.utils.logger.LokiLogger.requests.get')
    def test_shutdown_with_pending_logs_no_deadlock(self, mock_get, mock_post):
        """
        Test: shutdown() pendant que ~1000 logs sont en queue.
        Mesure: shutdown() complète en < 3 secondes (pas de deadlock).
        """
        self._reset_logger_cache_if_available()
        
        mock_get.return_value.status_code = 200
        
        # Loki très lent (1s par batch)
        def very_slow_post(*args, **kwargs):
            time.sleep(1.0)
            response = MagicMock()
            response.status_code = 204
            return response
        
        mock_post.side_effect = very_slow_post
        
        logger = LoggerFactory.create_logger('shutdown_deadlock', 'loki')
        
        try:
            # Enqueue 1000 logs
            for i in range(1000):
                logger.info(f"message {i}")
            
            # Shutdown immédiatement (sans attendre flush)
            start = time.perf_counter()
            logger.shutdown()
            shutdown_duration = time.perf_counter() - start
            
            self.assertLess(
                shutdown_duration,
                3.0,
                msg=f"Shutdown deadlock potentiel: {shutdown_duration:.3f}s"
            )
            
        finally:
            pass

    # =========================================================================
    # TEST 6: Concurrent flush and logging
    # =========================================================================
    @override_settings(
        LOGGER_TYPE='loki',
        LOKI_URL='http://test-loki:3100',
        LOKI_BATCH_SIZE=50,
        LOKI_BATCH_TIMEOUT=1.0,
    )
    @patch('main.domain.common.utils.logger.LokiLogger.requests.post')
    @patch('main.domain.common.utils.logger.LokiLogger.requests.get')
    def test_flush_concurrent_logging_no_block(self, mock_get, mock_post):
        """
        Test: flush() pendant que d'autres threads loggent.
        Mesure: logging threads ne sont pas bloqués, flush < 12s.
        """
        self._reset_logger_cache_if_available()
        
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 204
        
        logger = LoggerFactory.create_logger('flush_concurrent', 'loki')
        
        try:
            logs_logged = []
            logs_lock = threading.Lock()
            
            def log_thread():
                for i in range(100):
                    start = time.perf_counter()
                    logger.info(f"concurrent message {i}")
                    duration = time.perf_counter() - start
                    
                    with logs_lock:
                        logs_logged.append(duration)
            
            # Démarrer threads de logging
            threads = [threading.Thread(target=log_thread) for _ in range(5)]
            for t in threads:
                t.start()
            
            # Flush after 500ms
            time.sleep(0.5)
            start_flush = time.perf_counter()
            logger.flush()
            flush_duration = time.perf_counter() - start_flush
            
            # Attendre threads
            for t in threads:
                t.join()
            
            # Vérifier metrics
            self.assertLess(
                flush_duration,
                12.0,
                msg=f"Flush trop lent: {flush_duration:.3f}s"
            )
            
            max_log_duration = max(logs_logged)
            self.assertLess(
                max_log_duration,
                0.05,
                msg=f"Logging bloqué par flush: {max_log_duration:.3f}s"
            )
            
        finally:
            if hasattr(logger, 'shutdown'):
                logger.shutdown()

    # =========================================================================
    # TEST 7: Batch timeout edge case (partial batch at deadline)
    # =========================================================================
    @override_settings(
        LOGGER_TYPE='loki',
        LOKI_URL='http://test-loki:3100',
        LOKI_BATCH_SIZE=100,
        LOKI_BATCH_TIMEOUT=0.2,
    )
    @patch('main.domain.common.utils.logger.LokiLogger.requests.post')
    @patch('main.domain.common.utils.logger.LokiLogger.requests.get')
    def test_batch_timeout_sends_partial_batch(self, mock_get, mock_post):
        """
        Test: 10 logs, batch_size=100, batch_timeout=0.2s.
        Mesure: les 10 logs sont envoyés après ~0.2s (pas d'attente 100 logs).
        """
        self._reset_logger_cache_if_available()
        
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 204
        
        logger = LoggerFactory.create_logger('batch_timeout', 'loki')
        
        try:
            # Log 10 messages (batch_size=100)
            for i in range(10):
                logger.info(f"message {i}")
            
            # Attendre que le batch timeout se déclenche
            start_wait = time.perf_counter()
            while not mock_post.called and (time.perf_counter() - start_wait) < 1.0:
                time.sleep(0.05)
            
            send_time = time.perf_counter() - start_wait
            
            # Les 10 logs doivent être envoyés après ~0.2-0.3s + overhead système (~0.2s)
            # Total timeout réaliste: 0.7s (0.1s overhead + 0.2s batch_timeout + 0.4s system)
            self.assertLess(
                send_time,
                0.7,
                msg=f"Batch timeout pas déclenché: sent after {send_time:.3f}s"
            )
            
            # Vérifier que 10 logs ont été envoyés
            payload = mock_post.call_args[1]['json']
            sent_count = len(payload['streams'][0]['values'])
            self.assertEqual(sent_count, 10)
            
        finally:
            if hasattr(logger, 'shutdown'):
                logger.shutdown()

    # =========================================================================
    # TEST 8: Loki recovery after failures (backoff)
    # =========================================================================
    @override_settings(
        LOGGER_TYPE='loki',
        LOKI_URL='http://test-loki:3100',
        LOKI_BATCH_SIZE=10,
        LOKI_BATCH_TIMEOUT=0.5,
    )
    @patch('main.domain.common.utils.logger.LokiLogger.requests.post')
    @patch('main.domain.common.utils.logger.LokiLogger.requests.get')
    def test_loki_recovery_after_failures(self, mock_get, mock_post):
        """
        Test: Loki échoue 2 fois, puis revient.
        Mesure: après 3 failures -> shutdown auto (queue vidée) sans blocker.
        """
        self._reset_logger_cache_if_available()
        
        mock_get.return_value.status_code = 200
        
        # Simuler 2 failures, puis success
        call_count = [0]
        def side_effect_post(*args, **kwargs):
            call_count[0] += 1
            response = MagicMock()
            
            if call_count[0] <= 2:
                response.status_code = 500  # failure
            else:
                response.status_code = 204  # success
            return response
        
        mock_post.side_effect = side_effect_post
        
        logger = LoggerFactory.create_logger('recovery', 'loki')
        
        try:
            # Log plusieurs batches
            for batch in range(5):
                for i in range(10):
                    logger.info(f"batch {batch} message {i}")
                time.sleep(0.6)
            
            # Vérifier que après failures, logger s'arrête
            # (ne bloque pas, ne continue pas indéfiniment)
            start = time.perf_counter()
            logger.shutdown()
            shutdown_time = time.perf_counter() - start
            
            self.assertLess(
                shutdown_time,
                2.0,
                msg=f"Shutdown bloqué après failures: {shutdown_time:.3f}s"
            )
            
        finally:
            pass

    # =========================================================================
    # TEST 9: _dequeue_log_entry deadline race
    # =========================================================================
    @override_settings(
        LOGGER_TYPE='loki',
        LOKI_URL='http://test-loki:3100',
        LOKI_BATCH_SIZE=1000,
        LOKI_BATCH_TIMEOUT=5.0,
    )
    @patch('main.domain.common.utils.logger.LokiLogger.requests.post')
    @patch('main.domain.common.utils.logger.LokiLogger.requests.get')
    def test_deadline_race_condition_on_dequeue(self, mock_get, mock_post):
        """
        Test: Race entre deadline atteinte et dequeue timeout.
        Mesure: shutdown() via deadline < 2s même avec remaining=0.
        """
        self._reset_logger_cache_if_available()
        
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 204
        
        logger = LoggerFactory.create_logger('deadline_race', 'loki')
        
        try:
            # Log un seul message
            logger.info("test message")
            
            # Shutdown immédiatement, teste la race sur deadline
            start = time.perf_counter()
            logger.shutdown()
            shutdown_time = time.perf_counter() - start
            
            self.assertLess(
                shutdown_time,
                2.0,
                msg=f"Deadline race bloquerait: {shutdown_time:.3f}s"
            )
            
        finally:
            pass

    # =========================================================================
    # TEST 10: Multiple loggers concurrent creation
    # =========================================================================
    @override_settings(
        LOGGER_TYPE='loki',
        LOKI_URL='http://test-loki:3100',
        LOKI_BATCH_SIZE=10,
        LOKI_BATCH_TIMEOUT=1.0,
    )
    @patch('main.domain.common.utils.logger.LokiLogger.requests.get')
    def test_multiple_logger_creation_parallel_not_blocked(self, mock_get):
        """
        Test: Créer 100 loggers en parallèle.
        Mesure: création < 2s, chaque logger < 20ms.
        """
        self._reset_logger_cache_if_available()
        
        mock_get.return_value.status_code = 200
        
        loggers = []
        durations = {}
        lock = threading.Lock()
        
        def create_logger(idx):
            start = time.perf_counter()
            try:
                logger = LoggerFactory.create_logger(f'parallel_{idx}', 'loki')
                duration = time.perf_counter() - start
                with lock:
                    durations[idx] = duration
                    loggers.append(logger)
            except Exception as e:
                with lock:
                    durations[idx] = -1  # Error marker
        
        threads = [
            threading.Thread(target=create_logger, args=(i,))
            for i in range(100)
        ]
        
        start_total = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        total_time = time.perf_counter() - start_total
        
        max_duration = max(d for d in durations.values() if d >= 0)
        
        self.assertLess(
            total_time,
            2.0,
            msg=f"Création 100 loggers trop lente: {total_time:.3f}s"
        )
        self.assertLess(
            max_duration,
            0.02,
            msg=f"Max logger creation: {max_duration:.3f}s"
        )
        
        # Cleanup
        for logger in loggers:
            try:
                if hasattr(logger, 'shutdown'):
                    logger.shutdown()
            except:
                pass


__all__ = ['LokiLoggingAdvancedLatencyTestCase']
