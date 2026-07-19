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
