from main.utils.settings import Settings
from typing import Optional, Any


class BaseCache():
    """
    Classe de base pour les systèmes de cache.
    """

    def __init__(self):
        self.expiration_duration: float = Settings.get('LIMIT_CACHE_DEFAULT')