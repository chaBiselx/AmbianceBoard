"""
Implémentation d'un logger composite qui combine plusieurs loggers.
Permet d'envoyer les logs vers plusieurs destinations simultanément.
"""

from typing import List, Any
from .ILogger import ILogger


class CompositeLogger(ILogger):
    """
    Logger composite qui délègue les appels de logging à plusieurs loggers.
    Utile pour envoyer les logs vers plusieurs destinations (fichier + Loki par exemple).
    """
    
    def __init__(self, logger_name: str = 'composite', loggers: List[ILogger] = None):
        """
        Initialise le logger composite.
        
        Args:
            logger_name (str): Nom du logger composite
            loggers (List[ILogger]): Liste des loggers à utiliser
        """
        if not logger_name:
            raise ValueError("Le nom du logger ne peut pas être vide")
        
        self._logger_name = logger_name
        self._loggers = loggers or []
    
    def add_logger(self, logger: ILogger) -> None:
        """
        Ajoute un logger à la liste.
        
        Args:
            logger (ILogger): Logger à ajouter
        """
        if logger not in self._loggers:
            self._loggers.append(logger)
    
    def remove_logger(self, logger: ILogger) -> None:
        """
        Retire un logger de la liste.
        
        Args:
            logger (ILogger): Logger à retirer
        """
        if logger in self._loggers:
            self._loggers.remove(logger)
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau DEBUG"""
        for logger in self._loggers:
            try:
                logger.debug(message, *args, **kwargs)
            except Exception:
                # Continue avec les autres loggers même si un échoue
                continue
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau INFO"""
        for logger in self._loggers:
            try:
                logger.info(message, *args, **kwargs)
            except Exception:
                # Continue avec les autres loggers même si un échoue
                continue
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau WARNING"""
        for logger in self._loggers:
            try:
                logger.warning(message, *args, **kwargs)
            except Exception:
                # Continue avec les autres loggers même si un échoue
                continue
    
    def error(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau ERROR"""
        for logger in self._loggers:
            try:
                logger.error(message, *args, **kwargs)
            except Exception:
                # Continue avec les autres loggers même si un échoue
                continue
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau CRITICAL"""
        for logger in self._loggers:
            try:
                logger.critical(message, *args, **kwargs)
            except Exception:
                # Continue avec les autres loggers même si un échoue
                continue
    
    def exception(self, message: str, *args, exc_info: bool = True, **kwargs) -> None:
        """Log une exception avec la stack trace"""
        for logger in self._loggers:
            try:
                logger.exception(message, *args, exc_info=exc_info, **kwargs)
            except Exception:
                # Continue avec les autres loggers même si un échoue
                continue
    
    def flush(self) -> None:
        """
        Force l'envoi de tous les logs en attente pour tous les loggers.
        """
        for logger in self._loggers:
            try:
                if hasattr(logger, 'flush'):
                    logger.flush()
            except Exception:
                # Continue avec les autres loggers même si un échoue
                continue
    
    def shutdown(self) -> None:
        """
        Arrête proprement tous les loggers.
        """
        for logger in self._loggers:
            try:
                if hasattr(logger, 'shutdown'):
                    logger.shutdown()
            except Exception:
                # Continue avec les autres loggers même si un échoue
                continue
    
    @property
    def logger_name(self) -> str:
        """Retourne le nom du logger composite"""
        return self._logger_name
    
    @property
    def loggers(self) -> List[ILogger]:
        """Retourne la liste des loggers"""
        return self._loggers.copy()
    
    @property
    def logger_count(self) -> int:
        """Retourne le nombre de loggers"""
        return len(self._loggers)
    
    def __str__(self) -> str:
        """Représentation string du logger"""
        logger_types = [type(logger).__name__ for logger in self._loggers]
        return f"CompositeLogger(name='{self._logger_name}', loggers={logger_types})"
    
    def __repr__(self) -> str:
        """Représentation pour le debugging"""
        return f"CompositeLogger(logger_name='{self._logger_name}', logger_count={len(self._loggers)})"
    
    def __del__(self) -> None:
        """Destructeur pour s'assurer que tous les loggers sont arrêtés proprement"""
        try:
            self.shutdown()
        except Exception:
            pass