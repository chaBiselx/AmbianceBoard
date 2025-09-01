from abc import ABC, abstractmethod
from typing import List

class DomainProvider(ABC):
    """
    Abstract base class for domain providers.
    Defines the interface that all domain providers must implement.
    """
    @abstractmethod
    def get_domains(self) -> List[str]:
        """
        Fetches and returns a list of domains.
        This method must be implemented by subclasses.
        """
        pass
