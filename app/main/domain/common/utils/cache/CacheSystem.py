from django.core.cache import cache
from typing import Optional, Any
from .ICache import ICache
from .BaseCache import BaseCache


class CacheSystem(ICache, BaseCache):
    """
    Implémentation concrète de l'interface ICache utilisant le système de cache Django.
    Cette classe encapsule les fonctionnalités de cache pour une utilisation standardisée.
    """



    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        return cache.get(key)

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Stocke une valeur dans le cache"""
        cache.set(key, value, timeout or self.expiration_duration)

    def delete(self, key: str) -> None:
        """Supprime une valeur du cache"""
        cache.delete(key)



 
