"""
Utilitaires pour la validation et manipulation des UUID.

Ce module fournit des fonctions pour vérifier si une chaîne de caractères
est un UUID valide, avec ou sans extension de fichier.
"""

from pydub import AudioSegment
import os
import tempfile
import requests

class AudioDurationUtils:

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

            # Charge le fichier audio avec pydub
            audio = AudioSegment.from_file(file_path)

            return len(audio) / 1000.0  # Convertit les millisecondes en secondes
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
                # Charge le fichier audio avec pydub
                audio = AudioSegment.from_file(temp_file_path)
                
                # Calcule la durée en secondes
                return len(audio) / 1000.0
          
            finally:
                # Supprime le fichier temporaire
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        except Exception:
            return None
    
