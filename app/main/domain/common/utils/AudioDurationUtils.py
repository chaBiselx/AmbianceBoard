import os
import tempfile
import requests
from mutagen import File

class AudioDurationUtils:

    @staticmethod
    def _get_duration_from_metadata(file_path: str) -> float|None:
        audio_file = File(file_path)
        if audio_file is None or audio_file.info is None:
            return None
        return getattr(audio_file.info, "length", None)

    @staticmethod
    def get_duration_from_file(file_path: str) -> float|None:
        """
        Récupère la durée d'un fichier audio en secondes.
        
        Args:
            file_path (str): Chemin vers le fichier audio
            
        Returns:
            float: Durée en secondes
        """
        try:
            if not os.path.exists(file_path):
                return None

            return AudioDurationUtils._get_duration_from_metadata(file_path)
        except Exception:
            # En cas d'erreur (fichier corrompu, format non supporté, etc.)
            return None
    
    @staticmethod
    def get_duration_from_url_file(url_file: str) -> float|None:
        """
        Récupère la durée d'un fichier audio accessible via une URL.
        
        Args:
            url_file (str): URL du fichier audio
            
        Returns:
            float: Durée en secondes, ou None si impossible à déterminer
        """
        try:
            # Télécharge le fichier dans un fichier temporaire
            response = requests.get(url_file, stream=True, timeout=30)
            response.raise_for_status()
            
            # Crée un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_file:
                # Écrit le contenu par chunks pour les gros fichiers
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            try:
                return AudioDurationUtils._get_duration_from_metadata(temp_file_path)
          
            finally:
                # Supprime le fichier temporaire
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        except Exception:
            return None
    
