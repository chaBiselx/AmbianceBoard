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
        "url": "https://stream.radioparadise.com/mp3-192",
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
        self._ensure_debug_mode()

        max_delay_variants = self._parse_max_delays(options["max_delays"])
        audio_files = self._get_audio_files_or_fail()

        with transaction.atomic():
            user, user_created = self._ensure_fixture_user()
            soundboard, soundboard_created = self._ensure_public_fixture_soundboard(user)

            counters = {
                "playlists_created": 0,
                "playlist_links_created": 0,
                "musics_created": 0,
                "url_links_created": 0,
            }

            order = self._seed_audio_playlists(
                user=user,
                soundboard=soundboard,
                max_delay_variants=max_delay_variants,
                audio_files=audio_files,
                counters=counters,
            )
            self._seed_url_playlists(
                user=user,
                soundboard=soundboard,
                start_order=order,
                counters=counters,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Fixture seed_public_soundboard terminee | "
                f"user_created={user_created} "
                f"soundboard_created={soundboard_created} "
                f"playlists_created={counters['playlists_created']} "
                f"playlist_links_created={counters['playlist_links_created']} "
                f"musics_created={counters['musics_created']}"
                f" url_links_created={counters['url_links_created']}"
            )
        )

    def _ensure_debug_mode(self) -> None:
        if not settings.DEBUG:
            raise CommandError(
                "La commande seed_public_soundboard est reservee a DEBUG=1."
            )

    def _get_audio_files_or_fail(self) -> list[Path]:
        data_dir = Path(__file__).resolve().parent / "dataFile"
        audio_files = self._get_audio_files(data_dir)
        if audio_files:
            return audio_files

        raise CommandError(
            f"Aucun fichier audio trouve dans {data_dir}. "
            "Ajoutez des fichiers audio dans dataFile puis relancez la commande."
        )

    def _ensure_fixture_user(self):
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
        return user, user_created

    def _ensure_public_fixture_soundboard(self, user):
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

        return soundboard, soundboard_created

    def _seed_audio_playlists(
        self,
        user,
        soundboard,
        max_delay_variants: Iterable[int],
        audio_files: list[Path],
        counters: dict,
    ) -> int:
        order = 1
        for playlist_payload in self._iter_playlist_payloads(max_delay_variants):
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
            playlist, playlist_created = self._ensure_playlist(
                user=user,
                playlist_name=playlist_payload["name"],
                expected_values=expected_values,
            )
            if playlist_created:
                counters["playlists_created"] += 1

            if self._ensure_soundboard_playlist_link(soundboard, playlist, order):
                counters["playlist_links_created"] += 1

            counters["musics_created"] += self._attach_audio_files(playlist, audio_files)
            order += 1

        return order

    def _seed_url_playlists(self, user, soundboard, start_order: int, counters: dict) -> None:
        order = start_order
        for spec in URL_BUTTON_SPECS:
            url_playlist, playlist_created, link_created = self._ensure_url_button_playlist(
                user=user,
                soundboard=soundboard,
                order=order,
                playlist_name=spec["playlist_name"],
            )
            if playlist_created:
                counters["playlists_created"] += 1
            if link_created:
                counters["playlist_links_created"] += 1

            counters["url_links_created"] += self._attach_url_button(url_playlist, spec)
            order += 1

    def _ensure_playlist(self, user, playlist_name: str, expected_values: dict):
        playlist, playlist_created = Playlist.objects.get_or_create(
            user=user,
            name=playlist_name,
            defaults=expected_values,
        )
        self._reconcile_model_values(playlist, expected_values)
        return playlist, playlist_created

    def _ensure_soundboard_playlist_link(self, soundboard, playlist, order: int) -> bool:
        soundboard_link, link_created = SoundboardPlaylist.objects.get_or_create(
            SoundBoard=soundboard,
            Playlist=playlist,
            defaults={
                "order": order,
                "section": 1,
                "activable_by_player": True,
            },
        )

        expected_link_values = {
            "order": order,
            "section": 1,
            "activable_by_player": True,
        }
        self._reconcile_model_values(soundboard_link, expected_link_values)
        return link_created

    def _attach_audio_files(self, playlist, audio_files: list[Path]) -> int:
        musics_created = 0
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

        return musics_created

    def _reconcile_model_values(self, model_instance, expected_values: dict) -> None:
        changed_fields: list[str] = []
        for field_name, expected_value in expected_values.items():
            if getattr(model_instance, field_name) != expected_value:
                setattr(model_instance, field_name, expected_value)
                changed_fields.append(field_name)

        if changed_fields:
            if hasattr(model_instance, "updated_at"):
                changed_fields.append("updated_at")
            model_instance.save(update_fields=changed_fields)

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
