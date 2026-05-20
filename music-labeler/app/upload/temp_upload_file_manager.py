import os
import tempfile
from pathlib import Path

from fastapi import HTTPException, UploadFile


class TempUploadFileManager:
    """Gestion du stockage temporaire des fichiers uploades."""

    def __init__(self, max_upload_size: int) -> None:
        self.max_upload_size = max_upload_size

    async def save(self, upload_file: UploadFile) -> str:
        """Sauvegarde l'upload en temporaire et retourne le chemin local."""
        suffix = Path(upload_file.filename or "").suffix
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            size = 0
            while chunk := await upload_file.read(1024 * 1024):
                size += len(chunk)
                if size > self.max_upload_size:
                    tmp.close()
                    os.unlink(tmp.name)
                    raise HTTPException(
                        status_code=413,
                        detail=f"Fichier trop volumineux. Taille max : {self.max_upload_size // (1024 * 1024)} Mo",
                    )
                tmp.write(chunk)
            return tmp.name

    @staticmethod
    def cleanup(tmp_path: str) -> None:
        """Supprime le fichier temporaire s'il existe."""
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
