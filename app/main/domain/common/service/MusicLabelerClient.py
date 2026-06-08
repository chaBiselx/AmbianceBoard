import os

import requests

from main.architecture.persistence.models.Music import Music
from main.domain.common.utils.settings import Settings


class MusicLabelerClient:
    """Client HTTP responsable des appels au microservice music-labeler."""

    def __init__(self) -> None:
        self.base_url = Settings.get('MUSIC_LABELER_URL')
        self.timeout = 120
        token = Settings.get('MUSIC_LABELER_TOKEN', '')
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    def analyze(self, music: Music) -> dict:
        """Envoie un fichier audio au microservice music-labeler."""
        if not music.file or not os.path.exists(music.file.path):
            raise FileNotFoundError(f"Fichier audio introuvable : {music.file.name}")

        try:
            with open(music.file.path, 'rb') as file_handle:
                response = requests.post(
                    f"{self.base_url}/label",
                    files={'file': (os.path.basename(music.file.name), file_handle, 'audio/*')},
                    params={'top_k': 4},
                    headers=self.headers,
                    timeout=self.timeout,
                )
            response.raise_for_status()
        except requests.ConnectionError:
            raise ConnectionError('Service music-labeler indisponible')
        except requests.Timeout:
            raise TimeoutError("Timeout lors de l'analyse")
        except requests.RequestException as error:
            raise RuntimeError(str(error))

        return response.json()

    def is_service_healthy(self) -> bool:
        """Vérifie si le microservice music-labeler est accessible."""
        try:
            response = requests.get(f"{self.base_url}/health", headers=self.headers, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False