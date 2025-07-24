"""
Factory pour créer des instances de logger.
Permet une création centralisée et configurée des loggers.
"""

from django.conf import settings
from typing import Optional
from .ILogger import ILogger
from .LoggerFile import LoggerFile
from .MemoryLogger import MemoryLogger


class LoggerFactory:
    """
    Factory pour créer des instances de logger.
    Permet de centraliser la création et la configuration des loggers.
    """
    
    @staticmethod
    def create_logger(logger_name: str = 'home', logger_type: str = 'file') -> ILogger:
        """
        Crée une instance de logger selon le type spécifié.
        
        Args:
            logger_name (str): Nom du logger à créer
            logger_type (str): Type de logger ('file', 'memory')
            
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
        else:
            raise ValueError(f"Type de logger non supporté: {logger_type}. Types supportés: 'file', 'memory'")
    
    @staticmethod
    def get_default_logger(logger_name: str = 'home') -> ILogger:
        """
        Retourne le logger par défaut de l'application.
        
        Returns:
            ILogger: Logger par défaut configuré pour 'home'
        """
        default_logger = settings.LOGGER_TYPE
        return LoggerFactory.create_logger(logger_name, default_logger)
