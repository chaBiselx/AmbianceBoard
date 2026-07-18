class YoutubeDownloadException(ValueError):
    """Base exception for YouTube async download domain errors."""

    translation_key = "errors.youtube.download.generic"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message())

    @classmethod
    def default_message(cls) -> str:
        return cls.translation_key


class YoutubeAudioTooLargeException(YoutubeDownloadException):
    translation_key = "errors.youtube.download.file_too_large"

    @classmethod
    def default_message(cls) -> str:
        return "Le poids du fichier est trop lourd."


class YoutubeAudioDownloadFailedException(YoutubeDownloadException):
    translation_key = "errors.youtube.download.failed"

    @classmethod
    def default_message(cls) -> str:
        return "Impossible de telecharger l'audio depuis cette URL"


class YoutubeAudioConvertedFileNotFoundException(YoutubeDownloadException):
    translation_key = "errors.youtube.download.converted_file_not_found"

    @classmethod
    def default_message(cls) -> str:
        return "Le fichier audio converti est introuvable"