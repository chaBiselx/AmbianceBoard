"""
Commande de fixture: python manage.py seed_public_soundboard

Cree un SoundBoard public de demonstration avec des playlists generees
par variantes de maxDelay, en alimentant chaque playlist avec les fichiers
trouves dans main/management/commands/dataFile.

Objectifs:
- idempotente (relancer la commande ne duplique pas les playlists/liaisons)
- extensible (configuration centralisee pour ajouter des variantes)
"""

from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

from ._soundboard_seed_common import BaseSoundboardSeedCommand


FIXTURE_USER = {
    "username": "fixture_public_owner",
    "email": "fixture_public_owner@example.test",
    "password": "fixturepassword",
    "is_staff": False,
    "is_superuser": False,
    "isConfirmed": True,
}

FIXTURE_SOUNDBOARD_NAME = "Fixture Public SoundBoard"

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


class Command(BaseSoundboardSeedCommand):
    help = (
        "Cree un SoundBoard public avec playlists contenant les fichiers de dataFile "
        "et variantes maxDelay (0, 10)."
    )

    FIXTURE_USER = FIXTURE_USER
    FIXTURE_SOUNDBOARD_NAME = FIXTURE_SOUNDBOARD_NAME
    PLAYLIST_BLUEPRINTS = PLAYLIST_BLUEPRINTS
