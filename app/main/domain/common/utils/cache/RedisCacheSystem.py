import redis
import pickle
from typing import Optional, Any
from main.domain.common.utils.settings import Settings
from .ICache import ICache
from .BaseCache import BaseCache
from main.domain.common.utils.logger import LoggerFactory


class RedisCacheSystem(ICache, BaseCache):
    """
    Implémentation concrète de l'interface ICache utilisant Redis directement.
    Cette classe encapsule les fonctionnalités de cache Redis pour une utilisation standardisée.
    """

    def __init__(self):
        super().__init__()
        self._redis_client = None
        self.logger = LoggerFactory.get_default_logger()

    @property
    def redis_client(self) -> redis.Redis:
        """
        Propriété pour obtenir le client Redis (lazy loading avec singleton).
        Crée la connexion uniquement au premier accès.
        """
        if self._redis_client is None:
            self._redis_client = redis.Redis(
                host=Settings.get("REDIS_HOST"),
                port=Settings.get("REDIS_PORT"),
                password=Settings.get("REDIS_PASSWORD"),
                db=Settings.get("REDIS_DB"),
                decode_responses=False  # On garde False pour pouvoir stocker des objets sérialisés
            )
        return self._redis_client

    def _serialize(self, value: Any) -> bytes:
        """Sérialise une valeur Python en bytes pour le stockage Redis"""
        return pickle.dumps(value)

    def _deserialize(self, value: bytes) -> Any:
        """Désérialise des bytes Redis en valeur Python"""
        if value is None:
            return None
        return pickle.loads(value)

    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache Redis"""
        try:
            value = self.redis_client.get(key)
            return self._deserialize(value)
        except (redis.RedisError, pickle.PickleError) as e:
            self.logger.error(f"Erreur lors de la récupération de la clé '{key}': {e}")
            # Log l'erreur si nécessaire
            return None

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Stocke une valeur dans le cache Redis"""
        try:
            serialized_value = self._serialize(value)
            expiration = timeout if timeout is not None else self.expiration_duration
            
            if expiration:
                self.redis_client.setex(key, int(expiration), serialized_value)
            else:
                self.redis_client.set(key, serialized_value)
        except (redis.RedisError, pickle.PickleError) as e:
            # Log l'erreur si nécessaire
            self.logger.error(f"Erreur lors du stockage de la clé'{key}': {e}")

    def delete(self, key: str) -> None:
        """Supprime une valeur du cache Redis"""
        try:
            self.redis_client.delete(key)
        except redis.RedisError as e:
            # Log l'erreur si nécessaire
            self.logger.error(f"Erreur lors de la suppression de la clé '{key}': {e}")

    def exists(self, key: str) -> bool:
        """Vérifie si une clé existe dans Redis"""
        try:
            return bool(self.redis_client.exists(key))
        except redis.RedisError as e:
            self.logger.error(f"Erreur lors de la vérification de la clé '{key}': {e}")
            return False

    def clear(self) -> None:
        """Vide tout le cache Redis (attention: vide toute la base Redis)"""
        try:
            self.redis_client.flushdb()
        except redis.RedisError as e:
            self.logger.error(f"Erreur lors du vidage du cache: {e}")

    def get_ttl(self, key: str) -> Optional[int]:
        """Récupère le TTL (Time To Live) d'une clé en secondes"""
        try:
            ttl = self.redis_client.ttl(key)
            return ttl if ttl >= 0 else None
        except redis.RedisError as e:
            self.logger.error(f"Erreur lors de la récupération du TTL de la clé '{key}': {e}")
            return None

    def close(self) -> None:
        """Ferme la connexion Redis"""
        if self._redis_client is not None:
            try:
                self._redis_client.close()
                self._redis_client = None
            except redis.RedisError as e:
                self.logger.error(f"Erreur lors de la fermeture de la connexion Redis: {e}")
