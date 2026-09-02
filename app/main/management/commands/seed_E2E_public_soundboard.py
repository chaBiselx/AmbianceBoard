"""
Commande de fixture: python manage.py seed_E2E_public_soundboard

Cree un SoundBoard public dedie aux tests E2E avec des playlists generees
par variantes de maxDelay, chaque playlist etant alimentee par un fichier
audio unique et deterministe issu de main/management/commands/dataFile.

Objectifs:
- idempotente (relancer la commande ne duplique pas les playlists/liaisons)
- extensible (configuration centralisee pour ajouter des variantes)
"""

from pathlib import Path

from django.core.files import File
from django.core.management.base import CommandError

from main.architecture.persistence.models.Music import Music
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

from ._soundboard_seed_common import BaseSoundboardSeedCommand


FIXTURE_USER = {
    "username": "E2E_public_owner",
    "email": "E2E_public_owner@example.test",
    "password": "fixturepassword",
    "is_staff": False,
    "is_superuser": False,
    "isConfirmed": True,
}

FIXTURE_SOUNDBOARD_NAME = "E2E_Test_Soundboard_Public"

# Ajouter une nouvelle entree ici pour ajouter facilement une famille de playlist.
PLAYLIST_BLUEPRINTS = (
    {
        "base_name": "Fixture Instant",
        "type_playlist": PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name,
        "color": "#1f7a8c",
        "color_text": "#ffffff",
        "audio_file_name": "Test_Tone_3.mp3",
    },
    {
        "base_name": "Fixture Ambient",
        "type_playlist": PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name,
        "color": "#1f7a8c",
        "color_text": "#ffffff",
        "audio_file_name": "Test_Tone_10.mp3",
    },
    {
        "base_name": "Fixture Music",
        "type_playlist": PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        "color": "#264653",
        "color_text": "#ffffff",
        "audio_file_name": "Test_Tone_30.mp3",
    },
)


class Command(BaseSoundboardSeedCommand):
    help = (
        "E2E Cree un SoundBoard public avec playlists contenant les fichiers de dataFile "
        "et variantes maxDelay (0, 10)."
    )

    FIXTURE_USER = FIXTURE_USER
    FIXTURE_SOUNDBOARD_NAME = FIXTURE_SOUNDBOARD_NAME
    PLAYLIST_BLUEPRINTS = PLAYLIST_BLUEPRINTS

    def _attach_audio_files_for_playlist(
        self, playlist, playlist_payload: dict, audio_files: list[Path]
    ) -> int:
        audio_file = self._get_blueprint_audio_file(
            audio_files, playlist_payload["audio_file_name"]
        )
        return self._attach_audio_file(playlist, audio_file)

    def _get_blueprint_audio_file(
        self, audio_files: list[Path], audio_file_name: str
    ) -> Path:
        for audio_file in audio_files:
            if audio_file.name == audio_file_name:
                return audio_file

        raise CommandError(
            f"Fichier audio fixture introuvable: {audio_file_name}. "
            "Verifiez le contenu de dataFile."
        )

    def _attach_audio_file(self, playlist, audio_file: Path) -> int:
        source_stem = audio_file.stem[:63]
        existing_music = Music.objects.filter(playlist=playlist).first()
        if existing_music and existing_music.fileName == source_stem:
            Music.objects.filter(playlist=playlist).exclude(pk=existing_music.pk).delete()
            return 0

        Music.objects.filter(playlist=playlist).delete()
        with audio_file.open("rb") as file_handle:
            Music.objects.create(
                playlist=playlist,
                file=File(file_handle, name=audio_file.name),
                alternativeName=f"E2E {audio_file.stem}",
            )
        return 1
