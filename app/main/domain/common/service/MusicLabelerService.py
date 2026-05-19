import os
import requests
from typing import Optional
from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.Track import Track
from main.architecture.persistence.models.TrackLabel import TrackLabel
from main.architecture.persistence.repository.TrackLabelRepository import TrackLabelRepository
from main.domain.common.utils.settings import Settings


class MusicLabelerService:
    MIN_CONFIDENCE_TO_SAVE = 0.1  # Seuil de confiance minimum pour conserver un label
    """
    Service responsable de la communication avec le microservice music-labeler
    et de la persistance des labels IA pour les tracks.
    """

    def __init__(self) -> None:
        self.repository = TrackLabelRepository()
        self.base_url = Settings.get('MUSIC_LABELER_URL')
        self.timeout = 120
        token = Settings.get('MUSIC_LABELER_TOKEN', '')
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    def analyze(self, music: Music) -> dict:
        """
        Envoie un fichier audio au microservice music-labeler et sauvegarde les labels.

        Args:
            music: L'instance Music à analyser.

        Returns:
            dict: La réponse brute du microservice (categories, bpm, duration_seconds, etc.)

        Raises:
            FileNotFoundError: Si le fichier audio n'existe pas sur le disque.
            ConnectionError: Si le microservice est indisponible.
            TimeoutError: Si l'analyse dépasse le timeout.
            RuntimeError: Pour toute autre erreur du microservice.
        """
        if not music.file or not os.path.exists(music.file.path):
            raise FileNotFoundError(f"Fichier audio introuvable : {music.file.name}")

        try:
            with open(music.file.path, 'rb') as f:
                response = requests.post(
                    f"{self.base_url}/label",
                    files={'file': (os.path.basename(music.file.name), f, 'audio/*')},
                    params={'top_k': 4},
                    headers=self.headers,
                    timeout=self.timeout,
                )
            response.raise_for_status()
        except requests.ConnectionError:
            raise ConnectionError("Service music-labeler indisponible")
        except requests.Timeout:
            raise TimeoutError("Timeout lors de l'analyse")
        except requests.RequestException as e:
            raise RuntimeError(str(e))

        data = response.json()
        self._save_from_response(music.track_ptr, data)
        return data

    def analyze_by_id(self, music_id: int) -> dict:
        """
        Analyse une musique par son ID.

        Args:
            music_id: L'ID de la Music.

        Returns:
            dict: La réponse brute du microservice.

        Raises:
            Music.DoesNotExist: Si la musique n'existe pas.
        """
        music = Music.objects.get(id=music_id)
        return self.analyze(music)

    def has_labels(self, track: Track) -> bool:
        """Vérifie si une track a déjà été labélisée."""
        return self.repository.has_labels(track)

    def get_labels(self, track: Track) -> list[TrackLabel]:
        """Retourne les labels d'une track."""
        return list(self.repository.get_labels_for_track(track))

    def get_playlist_labels(self, playlist) -> list[dict]:
        """
        Retourne les labels agrégés d'une playlist (top labels de toutes ses tracks).
        """
        return self.repository.get_top_labels_for_playlist(playlist)

    def get_playlist_categories(self, playlist) -> list[dict]:
        """
        Retourne les catégories dominantes d'une playlist.
        """
        return self.repository.get_playlist_categories(playlist)

    def get_labels_grouped_by_track(self, track_ids: list[int]) -> dict[int, dict]:
        """
        Retourne les labels groupés par track au format catégorie.
        Structure: {track_id: {category: {category_confidence, labels: [...]}}}
        """
        return self.repository.get_labels_grouped_by_track(track_ids)

    def _save_from_response(self, track: Track, data: dict) -> None:
        """Extrait les labels de la réponse du microservice et les sauvegarde."""
        if 'categories' not in data:
            return

        labels_to_save = []
        for cat_name, cat_data in data['categories'].items():
            cat_confidence = cat_data.get('category_confidence', 0)
            for lbl in cat_data.get('labels', []):
                if(lbl['confidence'] < self.MIN_CONFIDENCE_TO_SAVE):
                    continue  # Ignorer les labels avec une confiance pondérée trop faible  
                labels_to_save.append({
                    'category': cat_name,
                    'label': lbl['label'],
                    'confidence': lbl['confidence'],
                })

        self.repository.save_labels(track, labels_to_save)

    def is_service_healthy(self) -> bool:
        """Vérifie si le microservice music-labeler est accessible."""
        try:
            response = requests.get(f"{self.base_url}/health", headers=self.headers, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
