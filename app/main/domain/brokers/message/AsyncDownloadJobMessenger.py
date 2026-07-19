from celery import shared_task
from main.architecture.persistence.repository.AsyncDownloadJobRepository import AsyncDownloadJobRepository
from django.utils.translation import gettext as _
from main.domain.common.exceptions.YoutubeDownloadException import YoutubeDownloadException
from main.domain.common.service.AsyncDownloadStrategyFactory import AsyncDownloadStrategyFactory
from main.domain.common.utils.logger import logger


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def process_async_download_job(
    self,
    job_uuid: str,
):
    job_repository = AsyncDownloadJobRepository()
    async_job = job_repository.get_by_uuid(job_uuid)

    if async_job is None:
        logger.warning(
            "AsyncDownloadJobMessenger: job not found job_uuid=%s",
            job_uuid,
        )
        raise ValueError("Job introuvable")

    playlist = async_job.playlist
    user = async_job.user

    job_repository.mark_downloading(async_job)

    logger.info(
        "AsyncDownloadJobMessenger: start job_uuid=%s playlist_uuid=%s user_id=%s source=%s",
        job_uuid,
        playlist.uuid,
        user.id,
        async_job.source,
    )

    if playlist.user_id != user.id:
        logger.warning(
            "AsyncDownloadJobMessenger: forbidden job_uuid=%s playlist_uuid=%s user_id=%s",
            job_uuid,
            playlist.uuid,
            user.id,
        )
        raise ValueError("Acces refuse")

    strategy = AsyncDownloadStrategyFactory().get_strategy(async_job.source)

    try:
        music = strategy.create_music(async_job)
        logger.info(
            "AsyncDownloadJobMessenger: success job_uuid=%s playlist_uuid=%s music_id=%s",
            job_uuid,
            playlist.uuid,
            music.id,
        )
        job_repository.mark_success(async_job)
        return {"music_id": music.id}
    except YoutubeDownloadException as exc:
        translated_message = _(exc.translation_key)
        logger.warning(
            "AsyncDownloadJobMessenger: youtube validation failed job_uuid=%s playlist_uuid=%s user_id=%s err_key=%s err=%s",
            job_uuid,
            playlist.uuid,
            user.id,
            exc.translation_key,
            translated_message,
        )
        job_repository.mark_failed(async_job, translated_message)
        raise ValueError(translated_message) from exc
    except ValueError as exc:
        logger.warning(
            "AsyncDownloadJobMessenger: validation failed job_uuid=%s playlist_uuid=%s user_id=%s err=%s",
            job_uuid,
            playlist.uuid,
            user.id,
            exc,
        )
        job_repository.mark_failed(async_job, str(exc))
        raise
    except (ConnectionError, TimeoutError) as exc:
        logger.warning(
            "AsyncDownloadJobMessenger: network error job_uuid=%s playlist_uuid=%s user_id=%s err=%s",
            job_uuid,
            playlist.uuid,
            user.id,
            exc,
        )
        raise self.retry(exc=exc)
    except Exception as exc:
        logger.error(
            "AsyncDownloadJobMessenger: unexpected error job_uuid=%s playlist_uuid=%s user_id=%s err=%s",
            job_uuid,
            playlist.uuid,
            user.id,
            exc,
        )
        job_repository.mark_failed(async_job, str(exc))
        raise
