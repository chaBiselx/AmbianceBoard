import os
import subprocess
import tempfile
from mutagen import File
from main.domain.common.utils.settings import Settings
from main.domain.common.utils.logger import LoggerFactory

class AudioBitrateReducer:
    def __init__(self, input_file):
        """Initialise la classe avec le chemin du fichier audio."""
        self.input_file = input_file
        self.audio_loaded = False
        self.extension = os.path.splitext(input_file)[1].lower().replace(".", "")
        self.bitrate = None

        # Configuration du logger
        self.logger = LoggerFactory.get_default_logger()

    def load_audio(self):
        """Charge le fichier audio."""
        try:
            audio_file = File(self.input_file)
            self.audio_loaded = audio_file is not None and audio_file.info is not None
            if not self.audio_loaded:
                raise RuntimeError("format audio non supporté")
            self.logger.info(f"Fichier chargé : {self.input_file}")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du fichier : {e}")

    def get_bitrate(self):
        """Obtient le bitrate actuel via ffmpeg."""
        try:
            audio_file = File(self.input_file)
            bitrate = getattr(getattr(audio_file, "info", None), "bitrate", None)
            if bitrate is None:
                return None
            self.bitrate = bitrate // 1000
            self.logger.debug(f"Bitrate actuel : {self.bitrate} kbps")
            return self.bitrate
        except Exception as e:
            self.logger.error(f"Erreur lors de l'obtention du bitrate : {e}")
        return None

    def reduce_bitrate(self, output_file=None):
        """Réduit le bitrate du fichier audio si nécessaire et conserve l'extension."""
        target_bitrate=Settings.get('AUDIO_BITRATE_REDUCER_TARGET_BITRATE')
        if not self.audio_loaded:
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

        temporary_output_file = None
        try:
            ffmpeg_output_file = output_file
            if os.path.abspath(output_file) == os.path.abspath(self.input_file):
                output_directory = os.path.dirname(self.input_file) or "."
                descriptor, temporary_output_file = tempfile.mkstemp(suffix=f".{self.extension}", dir=output_directory)
                os.close(descriptor)
                ffmpeg_output_file = temporary_output_file

            result = subprocess.run(
                ["ffmpeg", "-y", "-i", self.input_file, "-b:a", f"{target_bitrate}k", ffmpeg_output_file],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                check=False
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or "conversion ffmpeg impossible")

            if temporary_output_file is not None:
                os.replace(temporary_output_file, output_file)

            self.logger.info(f"Fichier exporté avec un bitrate de {target_bitrate} kbps : {output_file}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exportation : {e}")
            if temporary_output_file is not None and os.path.exists(temporary_output_file):
                os.remove(temporary_output_file)


# # Exemple d'utilisation
# if __name__ == "__main__":
#     input_file = "input.mp3"  # Remplacez par votre fichier
#     reducer = AudioBitrateReducer(input_file)
#     reducer.load_audio()
#     reducer.reduce_bitrate()
