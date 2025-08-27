
from abc import ABC, abstractmethod
from typing import Any, Optional


class ICache(ABC):
    """
    Interface abstraite pour le système de caching.
    Cette interface définit les méthodes que tout cache doit implémenter.
    """


    @abstractmethod
    def get(self, key: str) -> Any:
        """Récupère une valeur du cache"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Stocke une valeur dans le cache"""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Supprime une clé du cache"""
        pass
