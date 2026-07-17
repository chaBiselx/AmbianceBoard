import os
import uuid
from pathlib import Path
from typing import Any, Optional, Tuple

import yt_dlp
from yt_dlp.utils import DownloadError

from main.domain.common.service.youtube.IYoutubeDownloader import IYoutubeDownloader
from main.domain.common.utils.settings import Settings


class YtDlpYoutubeDownloader(IYoutubeDownloader):
    """Implementation IYoutubeDownloader basee sur yt-dlp."""

    def __init__(self) -> None:
        self.target_bitrate = str(Settings.get('AUDIO_BITRATE_REDUCER_TARGET_BITRATE'))

    def download_audio(
        self,
        url: str,
        temp_dir: str,
        max_filesize_bytes: Optional[int] = None,
    ) -> Tuple[str, str]:
        output_template = str(Path(temp_dir) / f"{uuid.uuid4()}_%(id)s.%(ext)s")

        options = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "socket_timeout": 20,
            "retries": 2,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": self.target_bitrate,
                }
            ],
        }

        if max_filesize_bytes is not None:
            options["max_filesize"] = max_filesize_bytes

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_path = ydl.prepare_filename(info)
        except DownloadError as exc:
            message = str(exc).lower()
            if "max-filesize" in message or "larger than" in message:
                raise ValueError("Le poids du fichier est trop lourd.") from exc
            raise ValueError("Impossible de telecharger l'audio depuis cette URL") from exc

        mp3_path = self._resolve_mp3_path(info, downloaded_path, temp_dir)
        if mp3_path is None:
            if max_filesize_bytes is not None and self._has_oversized_partial_file(temp_dir, max_filesize_bytes):
                raise ValueError("Le poids du fichier est trop lourd.")
            raise ValueError("Le fichier audio converti est introuvable")

        title = (info.get("title") if isinstance(info, dict) else None) or Path(mp3_path).stem
        return title.strip(), mp3_path

    def _resolve_mp3_path(self, info: Any, downloaded_path: str, temp_dir: str) -> Optional[str]:
        candidates = []

        # Cas nominal: prepare_filename sans extension post-process.
        candidates.append(f"{os.path.splitext(downloaded_path)[0]}.mp3")

        if isinstance(info, dict):
            # yt-dlp peut poser le chemin final dans requested_downloads/filepath.
            requested_downloads = info.get("requested_downloads") or []
            for item in requested_downloads:
                filepath = item.get("filepath")
                if not filepath:
                    continue
                candidates.append(filepath)
                candidates.append(f"{os.path.splitext(filepath)[0]}.mp3")

            info_filepath = info.get("filepath")
            if info_filepath:
                candidates.append(info_filepath)
                candidates.append(f"{os.path.splitext(info_filepath)[0]}.mp3")

        for candidate in candidates:
            if candidate and candidate.lower().endswith(".mp3") and os.path.exists(candidate):
                return candidate

        # Fallback final: chercher le mp3 le plus recent du dossier temp.
        mp3_files = [path for path in Path(temp_dir).iterdir() if path.suffix.lower() == ".mp3"]
        if not mp3_files:
            return None

        latest_mp3 = max(mp3_files, key=lambda path: path.stat().st_mtime)
        return str(latest_mp3)

    def _has_oversized_partial_file(self, temp_dir: str, max_filesize_bytes: int) -> bool:
        for path in Path(temp_dir).iterdir():
            if path.is_file() and path.suffix.lower() in {".part", ".tmp"}:
                if path.stat().st_size >= max_filesize_bytes:
                    return True
        return False
