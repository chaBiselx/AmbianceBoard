from .BaseSettings import BaseSettings
from typing import Any


from django.conf import settings as django_settings_module

class AppSettings(BaseSettings):
    """
    Implémentation de BaseSettings pour Django.
    """

    def __init__(self):
        self._settings = django_settings_module

    def get(self, key: str, default: Any = None) -> Any:
        value_surcharge = self._get_surcharge_settings(key)
        if value_surcharge:
            return value_surcharge
        return getattr(self._settings, key, default)

    def _get_surcharge_settings(self, key: str) -> Any:
        # to implement with BDD/files/...
        return None

