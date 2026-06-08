from pathlib import Path

from fastapi import HTTPException


class UploadValidator:
    """Validation des contraintes sur les fichiers uploades."""

    allowed_extensions = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".webm"}

    def validate_extension(self, filename: str) -> None:
        ext = Path(filename).suffix.lower()
        if ext not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Format non supporte ({ext}). Formats acceptes : {', '.join(sorted(self.allowed_extensions))}",
            )
