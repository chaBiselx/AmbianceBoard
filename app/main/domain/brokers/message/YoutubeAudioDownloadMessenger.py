from celery import shared_task
from typing import Optional
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User
from main.domain.common.service.YoutubeAudioService import YoutubeAudioService
from main.domain.common.utils.logger import logger


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def download_youtube_audio(
    self,
    playlist_uuid: str,
    url: str,
    user_id: int,
    *extra_args,
):
    name = None
    if len(extra_args) > 0:
        # Compatibilite: certains appels envoient le nom en 4e argument positionnel.
        name = extra_args[0]
        
    logger.info(
        "YoutubeAudioDownloadMessenger: start playlist_uuid=%s user_id=%s",
        playlist_uuid,
        user_id,
    )

    try:
        playlist = Playlist.objects.get(uuid=playlist_uuid)
    except Playlist.DoesNotExist as exc:
        logger.warning(
            "YoutubeAudioDownloadMessenger: playlist not found playlist_uuid=%s",
            playlist_uuid,
        )
        raise ValueError("Playlist introuvable") from exc

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist as exc:
        logger.warning("YoutubeAudioDownloadMessenger: user not found user_id=%s", user_id)
        raise ValueError("Utilisateur introuvable") from exc

    if playlist.user_id != user.id:
        logger.warning(
            "YoutubeAudioDownloadMessenger: forbidden playlist_uuid=%s user_id=%s",
            playlist_uuid,
            user_id,
        )
        raise ValueError("Acces refuse")

    service = YoutubeAudioService(user=user)

    try:
        music = service.create_music_from_url(playlist=playlist, url=url, name=name)
        logger.info(
            "YoutubeAudioDownloadMessenger: success playlist_uuid=%s music_id=%s",
            playlist_uuid,
            music.id,
        )
        return {"music_id": music.id}
    except ValueError as exc:
        logger.warning(
            "YoutubeAudioDownloadMessenger: validation failed playlist_uuid=%s user_id=%s err=%s",
            playlist_uuid,
            user_id,
            exc,
        )
        raise
    except (ConnectionError, TimeoutError) as exc:
        logger.warning(
            "YoutubeAudioDownloadMessenger: network error playlist_uuid=%s user_id=%s err=%s",
            playlist_uuid,
            user_id,
            exc,
        )
        raise self.retry(exc=exc)
    except Exception as exc:
        logger.error(
            "YoutubeAudioDownloadMessenger: unexpected error playlist_uuid=%s user_id=%s err=%s",
            playlist_uuid,
            user_id,
            exc,
        )
        raise
