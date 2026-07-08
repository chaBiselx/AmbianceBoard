"""
Commande de fixture: python manage.py seed_public_soundboard

Cree un SoundBoard public de demonstration avec des playlists generees
par variantes de maxDelay, en alimentant chaque playlist avec les fichiers
trouves dans main/management/commands/dataFile.

Objectifs:
- idempotente (relancer la commande ne duplique pas les playlists/liaisons)
- extensible (configuration centralisee pour ajouter des variantes)
"""

from pathlib import Path
from typing import Iterable

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.LinkMusic import LinkMusic
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.UserPreference import UserPreference
from main.domain.common.enum.LinkMusicTypeEnum import LinkMusicTypeEnum
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum


FIXTURE_USER = {
    "username": "fixture_public_owner",
    "email": "fixture_public_owner@example.test",
    "password": "fixturepassword",
    "is_staff": False,
    "is_superuser": False,
    "isConfirmed": True,
}

FIXTURE_SOUNDBOARD_NAME = "Fixture Public SoundBoard"

# Ajouter/supprimer des valeurs ici pour faire evoluer les variantes maxDelay.
MAX_DELAY_VARIANTS: tuple[int, ...] = (0, 10)

# Ajouter une nouvelle entree ici pour ajouter facilement une famille de playlist.
PLAYLIST_BLUEPRINTS = (
    {
        "base_name": "Fixture Instant",
        "type_playlist": PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name,
        "color": "#1f7a8c",
        "color_text": "#ffffff",
    },
    {
        "base_name": "Fixture Ambient",
        "type_playlist": PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name,
        "color": "#1f7a8c",
        "color_text": "#ffffff",
    },
    {
        "base_name": "Fixture Music",
        "type_playlist": PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        "color": "#264653",
        "color_text": "#ffffff",
    },
)

AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}

URL_BUTTON_SPECS = (
    {
        "playlist_name": "Fixture Instant - Tone Test URL",
        "name": "Tone Test (URL)",
        "url": "https://sample-files.com//downloads/audio/mp3/tone-test.mp3",
        "url_type": LinkMusicTypeEnum.FILE.name,
    },
    {
        "playlist_name": "Fixture Instant - Radio Paradise URL",
        "name": "Radio Paradise (Stream)",
        "url": "http://stream.radioparadise.com/mp3-192",
        "url_type": LinkMusicTypeEnum.STREAM.name,
    },
)


class Command(BaseCommand):
    help = (
        "Cree un SoundBoard public avec playlists contenant les fichiers de dataFile "
        "et variantes maxDelay (0, 10)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--max-delays",
            default=",".join(str(delay) for delay in MAX_DELAY_VARIANTS),
            help="Liste des maxDelay separes par des virgules (ex: 0,10,20).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "La commande seed_public_soundboard est reservee a DEBUG=1."
            )

        max_delay_variants = self._parse_max_delays(options["max_delays"])
        data_dir = Path(__file__).resolve().parent / "dataFile"
        audio_files = self._get_audio_files(data_dir)

        if not audio_files:
            raise CommandError(
                f"Aucun fichier audio trouve dans {data_dir}. "
                "Ajoutez des fichiers audio dans dataFile puis relancez la commande."
            )

        with transaction.atomic():
            user, user_created = User.objects.get_or_create(
                username=FIXTURE_USER["username"],
                defaults={
                    "email": FIXTURE_USER["email"],
                    "password": make_password(FIXTURE_USER["password"]),
                    "is_staff": FIXTURE_USER["is_staff"],
                    "is_superuser": FIXTURE_USER["is_superuser"],
                    "isConfirmed": FIXTURE_USER["isConfirmed"],
                },
            )
            if user_created:
                UserPreference.objects.get_or_create(user=user)

            soundboard, soundboard_created = SoundBoard.objects.get_or_create(
                user=user,
                name=FIXTURE_SOUNDBOARD_NAME,
                defaults={
                    "is_public": True,
                    "color": "#0f172a",
                    "colorText": "#ffffff",
                },
            )

            if not soundboard.is_public:
                soundboard.is_public = True
                soundboard.save(update_fields=["is_public", "updated_at"])

            playlists_created = 0
            playlist_links_created = 0
            musics_created = 0
            url_links_created = 0

            order = 1
            for playlist_payload in self._iter_playlist_payloads(max_delay_variants):
                playlist, playlist_created = Playlist.objects.get_or_create(
                    user=user,
                    name=playlist_payload["name"],
                    defaults={
                        "typePlaylist": playlist_payload["type_playlist"],
                        "useSpecificColor": True,
                        "color": playlist_payload["color"],
                        "colorText": playlist_payload["color_text"],
                        "volume": 75,
                        "is_copiable": True,
                        "useSpecificDelay": playlist_payload["use_specific_delay"],
                        "maxDelay": playlist_payload["max_delay"],
                    },
                )

                # Reconciliation pour garder la fixture coherente entre les executions.
                changed = False
                expected_values = {
                    "typePlaylist": playlist_payload["type_playlist"],
                    "useSpecificColor": True,
                    "color": playlist_payload["color"],
                    "colorText": playlist_payload["color_text"],
                    "volume": 75,
                    "is_copiable": True,
                    "useSpecificDelay": playlist_payload["use_specific_delay"],
                    "maxDelay": playlist_payload["max_delay"],
                }
                for field_name, expected_value in expected_values.items():
                    if getattr(playlist, field_name) != expected_value:
                        setattr(playlist, field_name, expected_value)
                        changed = True

                if changed:
                    playlist.save()

                if playlist_created:
                    playlists_created += 1

                link, link_created = SoundboardPlaylist.objects.get_or_create(
                    SoundBoard=soundboard,
                    Playlist=playlist,
                    defaults={
                        "order": order,
                        "section": 1,
                        "activable_by_player": True,
                    },
                )

                if not link_created:
                    link_changed = False
                    if link.order != order:
                        link.order = order
                        link_changed = True
                    if link.section != 1:
                        link.section = 1
                        link_changed = True
                    if not link.activable_by_player:
                        link.activable_by_player = True
                        link_changed = True
                    if link_changed:
                        link.save()
                else:
                    playlist_links_created += 1

                for audio_file in audio_files:
                    source_stem = audio_file.stem[:63]
                    exists = Music.objects.filter(
                        playlist=playlist,
                        fileName=source_stem,
                    ).exists()
                    if exists:
                        continue

                    with audio_file.open("rb") as file_handle:
                        Music.objects.create(
                            playlist=playlist,
                            file=File(file_handle, name=audio_file.name),
                            alternativeName=audio_file.stem,
                        )
                        musics_created += 1

                order += 1

            for spec in URL_BUTTON_SPECS:
                url_playlist, playlist_created, link_created = self._ensure_url_button_playlist(
                    user=user,
                    soundboard=soundboard,
                    order=order,
                    playlist_name=spec["playlist_name"],
                )
                if playlist_created:
                    playlists_created += 1
                if link_created:
                    playlist_links_created += 1

                url_links_created += self._attach_url_button(url_playlist, spec)
                order += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Fixture seed_public_soundboard terminee | "
                f"user_created={user_created} "
                f"soundboard_created={soundboard_created} "
                f"playlists_created={playlists_created} "
                f"playlist_links_created={playlist_links_created} "
                f"musics_created={musics_created}"
                f" url_links_created={url_links_created}"
            )
        )

    def _get_audio_files(self, data_dir: Path) -> list[Path]:
        if not data_dir.exists() or not data_dir.is_dir():
            return []

        return sorted(
            [
                file_path
                for file_path in data_dir.iterdir()
                if file_path.is_file() and file_path.suffix.lower() in AUDIO_EXTENSIONS
            ]
        )

    def _parse_max_delays(self, raw_values: str) -> tuple[int, ...]:
        parsed_values: list[int] = []

        for raw in raw_values.split(","):
            candidate = raw.strip()
            if not candidate:
                continue

            try:
                delay = int(candidate)
            except ValueError as exc:
                raise CommandError(
                    f"Valeur maxDelay invalide: {candidate}. Utiliser des entiers >= 0."
                ) from exc

            if delay < 0:
                raise CommandError(
                    f"Valeur maxDelay invalide: {candidate}. Utiliser des entiers >= 0."
                )

            parsed_values.append(delay)

        if not parsed_values:
            raise CommandError("Aucune valeur maxDelay fournie.")

        return tuple(sorted(set(parsed_values)))

    def _iter_playlist_payloads(self, max_delay_variants: Iterable[int]) -> Iterable[dict]:
        for blueprint in PLAYLIST_BLUEPRINTS:
            for max_delay in max_delay_variants:
                yield {
                    "name": f"{blueprint['base_name']} - delay {max_delay}s",
                    "type_playlist": blueprint["type_playlist"],
                    "color": blueprint["color"],
                    "color_text": blueprint["color_text"],
                    "max_delay": max_delay,
                    "use_specific_delay": max_delay > 0,
                }

    def _ensure_url_button_playlist(self, user, soundboard, order: int, playlist_name: str):
        playlist, playlist_created = Playlist.objects.get_or_create(
            user=user,
            name=playlist_name,
            defaults={
                "typePlaylist": PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name,
                "useSpecificColor": True,
                "color": "#8b0000",
                "colorText": "#ffffff",
                "volume": 75,
                "is_copiable": True,
                "useSpecificDelay": False,
                "maxDelay": 0,
            },
        )

        expected_values = {
            "typePlaylist": PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name,
            "useSpecificColor": True,
            "color": "#8b0000",
            "colorText": "#ffffff",
            "volume": 75,
            "is_copiable": True,
            "useSpecificDelay": False,
            "maxDelay": 0,
        }
        changed = False
        for field_name, expected_value in expected_values.items():
            if getattr(playlist, field_name) != expected_value:
                setattr(playlist, field_name, expected_value)
                changed = True
        if changed:
            playlist.save()

        soundboard_link, link_created = SoundboardPlaylist.objects.get_or_create(
            SoundBoard=soundboard,
            Playlist=playlist,
            defaults={
                "order": order,
                "section": 1,
                "activable_by_player": True,
            },
        )
        if not link_created:
            link_changed = False
            if soundboard_link.order != order:
                soundboard_link.order = order
                link_changed = True
            if soundboard_link.section != 1:
                soundboard_link.section = 1
                link_changed = True
            if not soundboard_link.activable_by_player:
                soundboard_link.activable_by_player = True
                link_changed = True
            if link_changed:
                soundboard_link.save()

        return playlist, playlist_created, link_created

    def _attach_url_button(self, playlist, spec: dict) -> int:
        link, created = LinkMusic.objects.get_or_create(
            playlist=playlist,
            url=spec["url"],
            defaults={
                "alternativeName": spec["name"],
                "urlType": spec["url_type"],
            },
        )

        if not created:
            changed = False
            if link.alternativeName != spec["name"]:
                link.alternativeName = spec["name"]
                changed = True
            if link.urlType != spec["url_type"]:
                link.urlType = spec["url_type"]
                changed = True
            if changed:
                link.save(update_fields=["alternativeName", "urlType", "updated_at"])

        return 1 if created else 0
