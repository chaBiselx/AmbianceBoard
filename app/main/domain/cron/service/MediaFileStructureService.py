import os
import uuid
from pathlib import Path

from django.conf import settings

from main.architecture.persistence.models.Music import Music
from main.domain.common.utils.logger import LoggerFactory


class MediaFileStructureService:
    def __init__(self):
        self.logger = LoggerFactory.get_default_logger()

    def normalize_music_files(self) -> tuple[int, int]:
        media_root = Path(settings.MEDIA_ROOT)
        music_dir = media_root / Music.MUSIC_FOLDER
        duplicated_dir = music_dir / "musics"
        moved_count = 0
        conflict_count = 0

        if not duplicated_dir.is_dir():
            self.logger.info(f"Media file structure is valid: {duplicated_dir} does not exist")
            return moved_count, conflict_count

        music_dir.mkdir(parents=True, exist_ok=True)
        for source in sorted(path for path in duplicated_dir.rglob("*") if path.is_file()):
            destination = music_dir / source.name
            if destination.exists():
                self.logger.info(
                    f"Destination already exists at {destination}; assigning a UUID to {source}"
                )
                while destination.exists():
                    destination = music_dir / f"{uuid.uuid4()}{source.suffix}"

            old_name = source.relative_to(media_root).as_posix()
            new_name = destination.relative_to(media_root).as_posix()
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, destination)
            try:
                Music.objects.filter(file=old_name).update(file=new_name)
            except Exception:
                os.replace(destination, source)
                raise

            moved_count += 1
            self.logger.info(f"Moved media file from {old_name} to {new_name}")

        for directory in sorted(
            (path for path in duplicated_dir.rglob("*") if path.is_dir()),
            key=lambda path: len(path.parts),
            reverse=True,
        ):
            if not any(directory.iterdir()):
                directory.rmdir()
        if not any(duplicated_dir.iterdir()):
            duplicated_dir.rmdir()

        self.logger.info(
            f"Media file structure check complete: {moved_count} file(s) normalized, "
            f"{conflict_count} conflict(s)"
        )
        return moved_count, conflict_count
