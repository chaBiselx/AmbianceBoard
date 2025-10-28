from main.domain.common.utils.settings import Settings
from typing import Optional
from .ICache import ICache
from .CacheSystem import CacheSystem
from .RedisCacheSystem import RedisCacheSystem


class CacheFactory:
    """
    Factory pour créer des instances de cache.
    Permet de centraliser la création et la configuration des caches.
    """
    
    @staticmethod
    def create_cache(cache_type: str = 'memory') -> ICache:
        """
        Crée une instance de cache selon le type spécifié.

        Args:
            cache_type (str): Type de cache ('memory')

        Returns:
            ICache: Instance du cache créé
        Raises:
            ValueError: Si le type de cache n'est pas supporté
        """
        cache_type = cache_type.lower()
        if cache_type == 'memory':
            return CacheSystem()
        elif cache_type == 'redis':
            return RedisCacheSystem()
        else:
            raise ValueError(f"Type de cache non supporté: {cache_type}. Type supporté: 'memory'")

    @staticmethod
    def get_default_cache() -> ICache:
        """
        Retourne le cache par défaut de l'application.

        Returns:
            ICache: Cache par défaut configuré
        """
        return CacheFactory.create_cache(Settings.get('CACHE_TYPE'))
