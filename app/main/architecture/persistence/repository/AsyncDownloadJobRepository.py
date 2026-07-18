from datetime import timedelta
from typing import Optional

from django.db.models import QuerySet
from django.utils import timezone

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.AsyncDownloadJob import AsyncDownloadJob
from main.domain.common.enum.AsyncDownloadJobStatusEnum import AsyncDownloadJobStatusEnum


class AsyncDownloadJobRepository:

    _ACTIVE_STATUSES = [
        AsyncDownloadJobStatusEnum.PENDING.name,
        AsyncDownloadJobStatusEnum.DOWNLOADING.name,
    ]

    def create(
        self,
        user: User,
        playlist: Playlist,
        url: str,
        source: str = "youtube",
        alternative_name: Optional[str] = None,
    ) -> AsyncDownloadJob:
        """Crée un job en statut PENDING."""
        return AsyncDownloadJob.objects.create(
            user=user,
            playlist=playlist,
            url=url,
            source=source,
            alternative_name=alternative_name,
            status=AsyncDownloadJobStatusEnum.PENDING.name,
        )
        
    def get_by_uuid(self, uuid: str) -> Optional[AsyncDownloadJob]:
        """Récupère un job par son UUID."""
        try:
            return AsyncDownloadJob.objects.get(uuid=uuid)
        except AsyncDownloadJob.DoesNotExist:
            return None

    def count_active(self, playlist: Playlist) -> int:
        """Retourne le nombre de jobs actifs (PENDING ou DOWNLOADING) pour une playlist."""
        return AsyncDownloadJob.objects.filter(
            playlist=playlist,
            status__in=self._ACTIVE_STATUSES,
        ).count()

    def set_task_id(self, job: AsyncDownloadJob, task_id: str) -> None:
        """Associe l'identifiant de tâche Celery au job après apply_async."""
        job.celery_task_id = task_id
        job.save(update_fields=["celery_task_id", "updated_at"])

    def mark_downloading(self, job: AsyncDownloadJob) -> None:
        """Passe le job en DOWNLOADING au début de l'exécution de la tâche Celery."""
        job.status = AsyncDownloadJobStatusEnum.DOWNLOADING.name
        job.save(update_fields=["status", "updated_at"])

    def mark_success(self, job: AsyncDownloadJob) -> None:
        """Passe le job en SUCCESS à la fin d'un téléchargement réussi."""
        job.status = AsyncDownloadJobStatusEnum.SUCCESS.name
        job.save(update_fields=["status", "updated_at"])

    def mark_failed(self, job: AsyncDownloadJob, error_message: str) -> None:
        """Passe le job en FAILED et conserve le message d'erreur."""
        job.status = AsyncDownloadJobStatusEnum.FAILED.name
        job.error_message = error_message
        job.save(update_fields=["status", "error_message", "updated_at"])

    def get_recent_jobs_for_user(self, user: User) -> QuerySet[AsyncDownloadJob]:
        """Récupère les jobs de l'utilisateur mis à jour sur les dernières 24h."""
        cutoff = timezone.now() - timedelta(hours=24)
        return AsyncDownloadJob.objects.filter(
            user=user,
            updated_at__gte=cutoff,
        ).select_related("playlist").order_by("-updated_at")

    def count_recent_jobs_for_user(self, user: User) -> int:
        """Compte les jobs de l'utilisateur mis à jour sur les dernières 24h."""
        cutoff = timezone.now() - timedelta(hours=24)
        return AsyncDownloadJob.objects.filter(
            user=user,
            updated_at__gte=cutoff,
        ).count()
