from abc import ABC, abstractmethod
from typing import Any


class ILogger(ABC):
    """
    Interface abstraite pour le système de logging.
    Cette interface définit les méthodes que tout logger doit implémenter.
    """
    
    @abstractmethod
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau DEBUG"""
        pass
    
    @abstractmethod
    def info(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau INFO"""
        pass
    
    @abstractmethod
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau WARNING"""
        pass
    
    @abstractmethod
    def error(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau ERROR"""
        pass
    
    @abstractmethod
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau CRITICAL"""
        pass
    
    @abstractmethod
    def exception(self, message: str, *args, exc_info: bool = True, **kwargs) -> None:
        """Log une exception avec la stack trace"""
        pass
