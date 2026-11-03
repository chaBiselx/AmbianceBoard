from .BaseEnum import BaseEnum


class AsyncDownloadJobStatusEnum(BaseEnum):
    """
    Statuts possibles d'un job de téléchargement asynchrone.

    - PENDING    : En attente dans la queue Celery
    - DOWNLOADING: Téléchargement en cours
    - SUCCESS    : Téléchargement terminé avec succès
    - FAILED     : Échec définitif (quota, URL invalide, erreur réseau épuisée…)
    """
    PENDING = "PENDING"
    DOWNLOADING = "DOWNLOADING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

    @classmethod
    def can_retry(cls, status: str) -> bool:
        """
        Indique si le job peut être relancé.

        Args:
            status: Statut stocké sur le job.

        Returns:
            bool: True si le job est en échec ou en attente, False sinon
        """
        return status in (cls.PENDING.name, cls.FAILED.name)