"""
Module de cache.
Fournit une interface unifiée pour le système de cache.
"""

from .ICache import ICache
from .CacheSystem import CacheSystem
from .CacheFactory import CacheFactory

# Instance globale pour une utilisation facile
cache = CacheFactory.get_default_cache()

__all__ = ['ICache', 'CacheSystem', 'CacheFactory', 'cache']
