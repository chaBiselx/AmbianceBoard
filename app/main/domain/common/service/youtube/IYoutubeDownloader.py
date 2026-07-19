from abc import ABC, abstractmethod
from typing import Optional, Tuple


class IYoutubeDownloader(ABC):
    """Contrat de telechargement audio depuis une URL video."""

    @abstractmethod
    def download_audio(
        self,
        url: str,
        temp_dir: str,
        max_filesize_bytes: Optional[int] = None,
    ) -> Tuple[str, str]:
        """Retourne un tuple (title, mp3_path)."""
        pass
