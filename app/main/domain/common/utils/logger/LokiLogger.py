"""
Implémentation du logger pour Loki/Grafana.
Cette implémentation envoie les logs directement à Loki via HTTP.
"""

import json
import time
import requests
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from queue import Queue, Empty
from .ILogger import ILogger
from main.domain.common.utils.settings import Settings


class LokiLogger(ILogger):
    """
    Implémentation concrète de l'interface ILogger qui envoie les logs à Loki.
    Cette classe gère l'envoi des logs en arrière-plan avec un système de queue.
    """
    
    def __init__(self, logger_name: str = 'main'):
        """
        Initialise le logger Loki.
        
        Args:
            logger_name (str): Nom du logger
            loki_url (str): URL de l'instance Loki
            labels (Dict[str, str], optional): Labels par défaut pour tous les logs
            batch_size (int): Nombre de logs à envoyer par batch
            batch_timeout (float): Timeout en secondes pour envoyer un batch partiel
        """
        if not logger_name:
            raise ValueError("Le nom du logger ne peut pas être vide")
        
        # Résolution des paramètres à partir des settings Django si non fournis
        loki_url = Settings.get('LOKI_URL') or 'http://loki:3100'
        batch_size = Settings.get('LOKI_BATCH_SIZE') or 10
        batch_timeout = Settings.get('LOKI_BATCH_TIMEOUT') or 5.0

        self._logger_name = logger_name
        # Normalisation de l'URL Loki (sans double slash)
        self._loki_url = loki_url + '/loki/api/v1/push'
        self._default_labels = {}
        self._batch_size = batch_size
        self._batch_timeout = batch_timeout
        
        # Queue pour les logs en attente d'envoi
        self._log_queue: Queue = Queue()
        
        # Indicateur d'arrêt - DOIT être défini avant de démarrer le thread
        self._shutdown = threading.Event()
        
        # Thread pour l'envoi en arrière-plan
        self._sender_thread = threading.Thread(target=self._sender_worker, daemon=True)
        self._sender_thread.start()
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau DEBUG"""
        self._log('debug', message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau INFO"""
        self._log('info', message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau WARNING"""
        self._log('warning', message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau ERROR"""
        self._log('error', message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau CRITICAL"""
        self._log('critical', message, *args, **kwargs)
    
    def exception(self, message: str, *args, exc_info: bool = True, **kwargs) -> None:
        """Log une exception avec la stack trace"""
        import traceback
        if exc_info:
            exc_text = traceback.format_exc()
            message = f"{message}\n{exc_text}"
        self._log('error', message, *args, **kwargs)
    
    def _log(self, level: str, message: str, *args, **kwargs) -> None:
        """
        Méthode interne pour traiter un log.
        
        Args:
            level (str): Niveau du log
            message (str): Message à logger
            *args: Arguments positionnels pour le formatage du message
            **kwargs: Arguments nommés additionnels
        """
        # Formatage du message si des arguments sont fournis
        if args:
            try:
                message = message % args
            except (TypeError, ValueError):
                # Si le formatage échoue, on garde le message original
                pass
        
        # Création de l'entrée de log
        timestamp = time.time_ns()  # Timestamp en nanosecondes pour Loki
        
        # Fusion des labels par défaut et spécifiques
        labels = self._default_labels.copy()
        # Labels standards Loki / application
        labels.setdefault('job', 'ambianceboard')
        # Ne surcharger 'service' que s'il n'est pas fourni par l'utilisateur
        labels.setdefault('service', self._logger_name)
        labels['level'] = level
        labels['logger'] = self._logger_name
        
        # Ajout de labels additionnels depuis kwargs
        if 'extra_labels' in kwargs:
            labels.update(kwargs['extra_labels'])
        
        # Création de l'entrée de log
        log_entry = {
            'timestamp': str(timestamp),
            'message': message,
            'labels': labels
        }
        
        # Ajout à la queue
        try:
            self._log_queue.put_nowait(log_entry)
        except Exception:
            # En cas d'erreur, on ne peut pas faire grand-chose sans créer de boucle infinie
            pass
    
    def _sender_worker(self) -> None:
        """
        Worker thread qui envoie les logs à Loki par batches.
        """
        batch = []
        last_send_time = time.time()
        
        while not self._shutdown.is_set():
            try:
                # Attendre un log avec un timeout
                try:
                    log_entry = self._log_queue.get(timeout=1.0)
                    batch.append(log_entry)
                except Empty:
                    # Timeout atteint, vérifier s'il faut envoyer un batch partiel
                    current_time = time.time()
                    if batch and (current_time - last_send_time) >= self._batch_timeout:
                        self._send_batch(batch)
                        batch = []
                        last_send_time = current_time
                    continue
                
                # Envoyer le batch s'il est plein
                if len(batch) >= self._batch_size:
                    self._send_batch(batch)
                    batch = []
                    last_send_time = time.time()
                    
            except Exception:
                # En cas d'erreur, continuer pour éviter d'arrêter le thread
                continue
        
        # Envoyer les logs restants avant de fermer
        if batch:
            self._send_batch(batch)
    
    def _send_batch(self, batch: List[Dict[str, Any]]) -> None:
        """
        Envoie un batch de logs à Loki.
        
        Args:
            batch (List[Dict[str, Any]]): Liste des logs à envoyer
        """
        if not batch:
            return
        
        try:
            # Grouper les logs par ensemble de labels
            streams = {}
            
            for log_entry in batch:
                labels_key = json.dumps(log_entry['labels'], sort_keys=True)
                if labels_key not in streams:
                    streams[labels_key] = {
                        'stream': log_entry['labels'],
                        'values': []
                    }
                streams[labels_key]['values'].append([
                    log_entry['timestamp'],
                    log_entry['message']
                ])
            
            # Construction du payload Loki
            payload = {
                'streams': list(streams.values())
            }
            
            # Envoi à Loki
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self._loki_url,
                json=payload,
                headers=headers,
                timeout=10.0
            )
            
            # Log du statut de l'envoi (seulement en cas d'erreur pour éviter les boucles)
            if response.status_code != 204:
                # En cas d'erreur, on ne peut pas utiliser le logger lui-même
                pass
                
        except Exception:
            # En cas d'erreur de réseau ou autre, on ne peut pas faire grand-chose
            # sans risquer de créer une boucle infinie de logs d'erreur
            pass
    
    def flush(self) -> None:
        """
        Force l'envoi de tous les logs en attente.
        Utile avant l'arrêt de l'application.
        """
        # Attendre que la queue soit vide (avec timeout)
        timeout = 10.0
        start_time = time.time()
        
        while not self._log_queue.empty() and (time.time() - start_time) < timeout:
            time.sleep(0.1)
    
    def shutdown(self) -> None:
        """
        Arrête proprement le logger.
        """
        self.flush()
        self._shutdown.set()
        if self._sender_thread.is_alive():
            self._sender_thread.join(timeout=5.0)
    
    @property
    def logger_name(self) -> str:
        """Retourne le nom du logger"""
        return self._logger_name
    
    @property
    def loki_url(self) -> str:
        """Retourne l'URL de Loki"""
        return self._loki_url
    
    def __str__(self) -> str:
        """Représentation string du logger"""
        return f"LokiLogger(name='{self._logger_name}', url='{self._loki_url}')"
    
    def __repr__(self) -> str:
        """Représentation pour le debugging"""
        return f"LokiLogger(logger_name='{self._logger_name}', loki_url='{self._loki_url}')"
    
    def __del__(self) -> None:
        """Destructeur pour s'assurer que le logger est arrêté proprement"""
        try:
            self.shutdown()
        except Exception:
            pass