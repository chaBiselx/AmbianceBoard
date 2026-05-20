import librosa
import numpy as np


class AudioFeatureExtractor:
    """Extraction des metadonnees audio de base."""

    @staticmethod
    def extract(audio: np.ndarray, sr: int) -> dict:
        """Extract basic audio features with librosa."""
        tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
        bpm = float(tempo) if isinstance(tempo, (int, float, np.floating)) else float(tempo[0])
        return {
            "bpm": round(bpm, 1),
            "duration_seconds": round(float(len(audio) / sr), 2),
        }
