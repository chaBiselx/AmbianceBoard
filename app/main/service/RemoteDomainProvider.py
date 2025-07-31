import requests
from typing import List
from main.utils.logger import logger

class RemoteDomainProvider:
    """
    Provides a list of domains from a remote URL.
    """
    def __init__(self, url: str):
        if not url:
            raise ValueError("URL cannot be empty.")
        self.url = url

    def get_domains(self) -> List[str]:
        """
        Fetches and returns a list of domains from the configured URL.
        Returns an empty list if an error occurs.
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Filter out empty lines
            return [domain for domain in response.text.splitlines() if domain]
        
        except requests.RequestException as e:
            logger.error(f"Error fetching domains from {self.url}: {e}")
            return []
