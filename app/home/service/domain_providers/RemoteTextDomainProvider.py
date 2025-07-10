import logging
import requests
from typing import List
from .BaseProvider import DomainProvider

logger = logging.getLogger("home")

class RemoteTextDomainProvider(DomainProvider):
    """
    Provides a list of domains from a remote URL serving a plain text file.
    Each line in the file is considered a domain.
    """
    def __init__(self, url: str):
        if not url:
            raise ValueError("URL cannot be empty.")
        self.url = url

    def get_domains(self) -> List[str]:
        """
        Fetches and returns a list of domains from the configured text file URL.
        Returns an empty list if an error occurs.
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return [domain for domain in response.text.splitlines() if domain]
        except requests.RequestException as e:
            logger.error(f"Error fetching domains from {self.url}: {e}")
            return []
