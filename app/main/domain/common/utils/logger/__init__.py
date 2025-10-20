"""
Module de logging.
Fournit une interface unifiée pour le système de logging.
"""

from .ILogger import ILogger
from .LoggerFile import LoggerFile
from .MemoryLogger import MemoryLogger
from .LokiLogger import LokiLogger
from .CompositeLogger import CompositeLogger
from .LoggerFactory import LoggerFactory

# Instance globale pour une utilisation facile
logger = LoggerFactory.get_default_logger()

__all__ = ['ILogger', 'LoggerFile', 'MemoryLogger', 'LokiLogger', 'CompositeLogger', 'LoggerFactory', 'logger']
