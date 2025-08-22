from django.conf import settings
from typing import Optional, Any


class BaseCache():
    """
    Classe de base pour les systèmes de cache.
    """

    def __init__(self):
        self.expiration_duration: float = settings.LIMIT_CACHE_DEFAULT