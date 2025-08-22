from abc import ABC, abstractmethod
from typing import Any


class BaseSettings(ABC):
    """
    Abstraction pour la gestion des settings de l'application.
    Permet d'utiliser différentes sources de configuration.
    """
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        pass
