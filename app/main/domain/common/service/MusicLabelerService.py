from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.Track import Track
from main.architecture.persistence.repository.TrackLabelRepository import TrackLabelRepository
from main.domain.common.service.MusicLabelerClient import MusicLabelerClient


class MusicLabelerService:
    MIN_CONFIDENCE_TO_SAVE = 0.1  # Seuil de confiance minimum pour conserver un label
    """
    Service responsable de l'orchestration d'une analyse et de la persistance
    des labels IA pour les tracks.
    """

    def __init__(self) -> None:
        self.repository = TrackLabelRepository()
        self.client = MusicLabelerClient()
        
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
        try:
            music = Music.objects.get(id=music_id)
        except Music.DoesNotExist:
            raise Music.DoesNotExist(f"Music avec id={music_id} introuvable")
        return self.analyze(music)

    def analyze(self, music: Music) -> dict:
        """Analyse une musique via le client HTTP puis persiste les labels."""
        data = self.client.analyze(music)
        self._save_from_response(music.track_ptr, data)
        return data

    def _save_from_response(self, track: Track, data: dict) -> None:
        """Extrait les labels de la réponse du microservice et les sauvegarde."""
        if 'categories' not in data:
            return

        labels_to_save = []
        for cat_name, cat_data in data['categories'].items():
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
        return self.client.is_service_healthy()
