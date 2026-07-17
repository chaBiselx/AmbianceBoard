import os
import shutil
import tempfile
import uuid
from math import isfinite
from typing import Optional, Tuple
from urllib.parse import urlparse

from django.core.files import File
from django.utils.text import slugify

from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.TrackRepository import TrackRepository
from main.domain.common.factory.UserParametersFactory import UserParametersFactory
from main.domain.common.service.youtube.IYoutubeDownloader import IYoutubeDownloader
from main.domain.common.service.youtube.YtDlpYoutubeDownloader import YtDlpYoutubeDownloader
from main.domain.common.utils.logger import logger



class YoutubeAudioService:
    """Service metier pour extraire et enregistrer un audio distant en MP3 local."""

    def __init__(self, user: User, downloader: Optional[IYoutubeDownloader] = None) -> None:
        self.user = user
        self.track_repository = TrackRepository()
        self.downloader = downloader or YtDlpYoutubeDownloader()

    def create_music_from_url(self, playlist: Playlist, url: str, name: Optional[str] = None) -> Music:
        if playlist.user_id != self.user.id:
            raise ValueError("Playlist introuvable")

        self._validate_url(url)

        self._check_playlist_limit(playlist)

        temp_dir = tempfile.mkdtemp(prefix="yt_audio_")
        try:
            title, mp3_path = self._download_audio(url=url, temp_dir=temp_dir)
            self._check_file_weight(mp3_path)
            title = name or title
            return self._save_music(playlist=playlist, title=title, file_path=mp3_path)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _download_audio(self, url: str, temp_dir: str) -> Tuple[str, str]:
        max_filesize_bytes = self._get_max_filesize_bytes()
        try:
            return self.downloader.download_audio(
                url=url,
                temp_dir=temp_dir,
                max_filesize_bytes=max_filesize_bytes,
            )
        except ValueError:
            raise
        except Exception as exc:
            logger.warning(f"YoutubeAudioService: download failed for url={url}: {exc}")
            raise ValueError("Impossible de telecharger l'audio depuis cette URL") from exc

    def _validate_url(self, url: str) -> None:
        if not url or not url.startswith("https://"):
            raise ValueError("L'URL doit commencer par https://")

        parsed = urlparse(url)
        if not parsed.netloc:
            raise ValueError("URL invalide")

    def _check_playlist_limit(self, playlist: Playlist) -> None:
        user_parameters = UserParametersFactory(self.user)
        limit_music_per_playlist = user_parameters.limit_music_per_playlist
        if self.track_repository.get_count(playlist) >= limit_music_per_playlist:
            raise ValueError(
                "Vous avez atteint la limite de musique par playlist ("
                + str(limit_music_per_playlist)
                + " max)."
            )

    def _check_file_weight(self, file_path: str) -> None:
        limit_weight_file = UserParametersFactory(self.user).limit_weight_file
        file_size_bytes = os.path.getsize(file_path)
        if file_size_bytes > limit_weight_file * 1024 * 1024:
            raise ValueError("Le poids du fichier est trop lourd.")

    def _get_max_filesize_bytes(self) -> Optional[int]:
        limit_weight_file = UserParametersFactory(self.user).limit_weight_file
        if isinstance(limit_weight_file, (int, float)) and isfinite(limit_weight_file):
            if limit_weight_file <= 0:
                raise ValueError("La limite de poids audio est invalide.")
            return int(limit_weight_file * 1024 * 1024)
        return None

    def _save_music(self, playlist: Playlist, title: str, file_path: str, name: Optional[str] = None) -> Music:
        base_name = str(uuid.uuid4())
        upload_file_name = f"{base_name}.mp3"

        music = Music()
        music.playlist = playlist
        music.alternativeName = slugify(title)[:255]

        with open(file_path, "rb") as source_file:
            django_file = File(source_file, name=upload_file_name)
            music.file = django_file
            music.save()

        return music
