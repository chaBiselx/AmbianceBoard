import logging
from pydub import AudioSegment
import os

class AudioBitrateReducer:
    def __init__(self, input_file):
        """Initialise la classe avec le chemin du fichier audio."""
        self.input_file = input_file
        self.audio = None
        self.extension = os.path.splitext(input_file)[1].lower().replace(".", "")
        self.bitrate = None

        # Configuration du logger
        self.logger = logging.getLogger('home')

    def load_audio(self):
        """Charge le fichier audio."""
        try:
            self.audio = AudioSegment.from_file(self.input_file)
            self.logger.info(f"Fichier chargé : {self.input_file}")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du fichier : {e}")

    def get_bitrate(self):
        """Obtient le bitrate actuel via ffmpeg."""
        import subprocess

        try:
            result = subprocess.run(
                ["ffmpeg", "-i", self.input_file],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True
            )
            for line in result.stderr.split('\n'):
                if "bitrate:" in line:
                    bitrate_str = line.split("bitrate:")[1].strip().split()[0]
                    self.bitrate = int(bitrate_str)
                    self.logger.debug(f"Bitrate actuel : {self.bitrate} kbps")
                    return self.bitrate
        except Exception as e:
            self.logger.error(f"Erreur lors de l'obtention du bitrate : {e}")
        return None

    def reduce_bitrate(self, output_file=None, target_bitrate=128):
        """Réduit le bitrate du fichier audio si nécessaire et conserve l'extension."""
        if self.audio is None:
            self.logger.debug("L'audio n'est pas chargé. Exécutez 'load_audio()' en premier.")
            return

        current_bitrate = self.get_bitrate()

        # Vérification du bitrate
        if current_bitrate is None:
            self.logger.error("Impossible de déterminer le bitrate. Arrêt.")
            return

        if current_bitrate <= target_bitrate:
            self.logger.debug(f"Le bitrate ({current_bitrate} kbps) est déjà inférieur ou égal à {target_bitrate} kbps. Aucune conversion nécessaire.")
            return

        # Génération du nom de sortie si non fourni
        if output_file is None:
            output_file = os.path.splitext(self.input_file)[0] + f".{self.extension}"

        try:
            self.audio.export(output_file, format=self.extension, bitrate=f"{target_bitrate}k")
            self.logger.info(f"Fichier exporté avec un bitrate de {target_bitrate} kbps : {output_file}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exportation : {e}")


# # Exemple d'utilisation
# if __name__ == "__main__":
#     input_file = "input.mp3"  # Remplacez par votre fichier
#     reducer = AudioBitrateReducer(input_file)
#     reducer.load_audio()
#     reducer.reduce_bitrate()
