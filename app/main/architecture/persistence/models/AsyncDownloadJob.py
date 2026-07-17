import uuid as uuid_lib

from django.conf import settings
from django.db import models
from main.architecture.persistence.models.Playlist import Playlist
from main.domain.common.enum.AsyncDownloadJobStatusEnum import AsyncDownloadJobStatusEnum


class AsyncDownloadJob(models.Model):
    """
    Suit le cycle de vie d'un téléchargement audio YouTube déclenché via Celery.

    Permet de :
    - Compter les jobs actifs (PENDING/DOWNLOADING) pour le contrôle de limite par playlist
    - Tracer l'avancement d'un téléchargement
    - Conserver le message d'erreur en cas d'échec définitif
    """

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid_lib.uuid4, editable=False, db_index=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="youtube_download_jobs",
    )
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name="youtube_download_jobs",
    )

    url = models.URLField(max_length=500)
    source = models.CharField(max_length=50, default="youtube", db_index=True)
    alternative_name = models.CharField(max_length=255, blank=True, null=True)

    celery_task_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=[(e.name, e.value) for e in AsyncDownloadJobStatusEnum],
        default=AsyncDownloadJobStatusEnum.PENDING.name,
        db_index=True,
    )
    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Async Download Job"
        verbose_name_plural = "Async Download Jobs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["playlist", "status"], name="idx_ytdljob_playlist_status"),
            models.Index(fields=["user", "status"], name="idx_ytdljob_user_status"),
        ]

    def __str__(self) -> str:
        return f"AsyncDownloadJob([{self.source}] {self.uuid}) [{self.status}]  {self.url}"
