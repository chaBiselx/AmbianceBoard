import logging
from typing import Optional, Any
from .ILogger import ILogger


class LoggerFile(ILogger):
    """
    Implémentation concrète de l'interface ILogger utilisant le système de logging Django.
    Cette classe encapsule les fonctionnalités de logging pour une utilisation standardisée.
    """
    
    def __init__(self, logger_name: str = 'home'):
        """
        Initialise le logger avec un nom spécifique.
        
        Args:
            logger_name (str): Nom du logger à utiliser (par défaut 'home')
            
        Raises:
            ValueError: Si le nom du logger est vide ou None
        """
        if not logger_name:
            raise ValueError("Le nom du logger ne peut pas être vide")
        
        self._logger_name = logger_name
        self._logger = logging.getLogger(logger_name)
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau DEBUG"""
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau INFO"""
        self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau WARNING"""
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau ERROR"""
        self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau CRITICAL"""
        self._logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, exc_info=True, **kwargs) -> None:
        """Log une exception avec la stack trace"""
        self._logger.error(message, *args, exc_info=exc_info, **kwargs)
    
    @property
    def logger(self) -> logging.Logger:
        """Retourne l'instance du logger pour un accès direct si nécessaire"""
        return self._logger
    
    @property
    def logger_name(self) -> str:
        """Retourne le nom du logger"""
        return self._logger_name
    
    def __str__(self) -> str:
        """Représentation string du logger"""
        return f"LoggerFile(name='{self._logger_name}')"
    
    def __repr__(self) -> str:
        """Représentation pour le debugging"""
        return f"LoggerFile(logger_name='{self._logger_name}')"

