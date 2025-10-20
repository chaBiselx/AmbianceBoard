"""
Factory pour créer des instances de logger.
Permet une création centralisée et configurée des loggers.
"""

from main.domain.common.utils.settings import Settings
from typing import Optional, Dict, Any
from .ILogger import ILogger
from .LoggerFile import LoggerFile
from .MemoryLogger import MemoryLogger
from .CompositeLogger import CompositeLogger
from .LokiLogger import LokiLogger


class LoggerFactory:
    """
    Factory pour créer des instances de logger.
    Permet de centraliser la création et la configuration des loggers.
    """
    
    @staticmethod
    def create_logger(logger_name: str = 'main', logger_type: str = 'file', **kwargs) -> ILogger:
        """
        Crée une instance de logger selon le type spécifié.
        
        Args:
            logger_name (str): Nom du logger à créer
            logger_type (str): Type de logger ('file', 'memory', 'loki')
            **kwargs: Arguments additionnels pour la configuration du logger
            
        Returns:
            ILogger: Instance du logger créé
            
        Raises:
            ValueError: Si le type de logger n'est pas supporté
        """
        logger_type = logger_type.lower()
        
        if logger_type == 'file':
            return LoggerFile(logger_name)
        elif logger_type == 'memory':
            return MemoryLogger(logger_name)
        elif logger_type == 'loki':
            return LokiLogger(
                logger_name=logger_name,
            )
        elif logger_type == 'composite':
            logger_types = kwargs.get('logger_types', ['file', 'loki'])
            loggers = []
            
            for sub_logger_type in logger_types:
                try:
                    # Créer chaque sous-logger avec les mêmes kwargs
                    sub_logger = LoggerFactory.create_logger(logger_name, sub_logger_type)
                    loggers.append(sub_logger)
                except Exception:
                    # Si un logger échoue, continuer avec les autres
                    continue
            return CompositeLogger(logger_name, loggers)
        else:
            raise ValueError(f"Type de logger non supporté: {logger_type}. Types supportés: 'file', 'memory', 'loki', 'composite'")
    
    
    @staticmethod
    def get_default_logger(logger_name: str = 'main') -> ILogger:
        """
        Retourne le logger par défaut de l'application.
        
        Returns:
            ILogger: Logger par défaut configuré pour 'main'
        """
        default_logger = Settings.get('LOGGER_TYPE')
        return LoggerFactory.create_logger(logger_name, default_logger)
