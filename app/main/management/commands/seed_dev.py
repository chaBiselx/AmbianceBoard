"""
Commande de développement : python manage.py seed_dev

Crée un utilisateur de test et 20 playlists de démonstration.
Disponible UNIQUEMENT si DEBUG=True (variable d'environnement DEBUG=1).
Idempotente : un second appel ne duplique rien.

Utilisateur créé  : dev / dev@dev.local  (mdp : devpassword)
Playlists créées  : 20 réparties sur les 3 types (Instant, Ambient, Music)
"""

from uuid import uuid4
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError


_DEV_USER = {
    "username": f"user_{uuid4().hex[:8]}",
    "email": f"{uuid4().hex[:8]}@example.test",
    "password": "devpassword",
    "is_staff": False,
    "is_superuser": False,
    "isConfirmed": True,
}

_PLAYLIST_NAMES = [
    # Instant (effets sonores)
    ("Coup d'épée",       "PLAYLIST_TYPE_INSTANT"),
    ("Tonnerre",          "PLAYLIST_TYPE_INSTANT"),
    ("Bruit de foule",    "PLAYLIST_TYPE_INSTANT"),
    ("Porte qui grince",  "PLAYLIST_TYPE_INSTANT"),
    ("Explosion",         "PLAYLIST_TYPE_INSTANT"),
    ("Clochette magique", "PLAYLIST_TYPE_INSTANT"),
    # Ambient (ambiances)
    ("Forêt nocturne",    "PLAYLIST_TYPE_AMBIENT"),
    ("Taverne animée",    "PLAYLIST_TYPE_AMBIENT"),
    ("Souterrain sombre", "PLAYLIST_TYPE_AMBIENT"),
    ("Mer agitée",        "PLAYLIST_TYPE_AMBIENT"),
    ("Village médiéval",  "PLAYLIST_TYPE_AMBIENT"),
    ("Marché oriental",   "PLAYLIST_TYPE_AMBIENT"),
    ("Salle du trône",    "PLAYLIST_TYPE_AMBIENT"),
    # Music (musiques)
    ("Bataille épique",   "PLAYLIST_TYPE_MUSIC"),
    ("Thème principal",   "PLAYLIST_TYPE_MUSIC"),
    ("Victoire",          "PLAYLIST_TYPE_MUSIC"),
    ("Mystère et intrigue","PLAYLIST_TYPE_MUSIC"),
    ("Romance",           "PLAYLIST_TYPE_MUSIC"),
    ("Exploration",       "PLAYLIST_TYPE_MUSIC"),
    ("Boss final",        "PLAYLIST_TYPE_MUSIC"),
]

_TYPE_COLORS = {
    "PLAYLIST_TYPE_INSTANT": ("#e74c3c", "#ffffff"),
    "PLAYLIST_TYPE_AMBIENT": ("#27ae60", "#ffffff"),
    "PLAYLIST_TYPE_MUSIC":   ("#2980b9", "#ffffff"),
}


class Command(BaseCommand):
    help = "Crée les données de développement (utilisateur + playlists). DEBUG=1 requis."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "La commande seed_dev est réservée à l'environnement de développement (DEBUG=1)."
            )

        from main.architecture.persistence.models.Playlist import Playlist
        from main.architecture.persistence.models.User import User
        from main.architecture.persistence.models.UserPreference import UserPreference

        # -- Utilisateur --------------------------------------------------------
        user, user_created = User.objects.get_or_create(
            username=_DEV_USER["username"],
            defaults={
                "email": _DEV_USER["email"],
                "password": make_password(_DEV_USER["password"]),
                "is_staff": _DEV_USER["is_staff"],
                "is_superuser": _DEV_USER["is_superuser"],
                "isConfirmed": _DEV_USER["isConfirmed"],
            },
        )

        if user_created:
            UserPreference.objects.get_or_create(user=user)
            self.stdout.write(self.style.SUCCESS(
                f"Utilisateur créé  : {user.username} ({user.email})"
            ))
        else:
            self.stdout.write(f"Utilisateur déjà existant : {user.username}")

        # -- Playlists ----------------------------------------------------------
        created_count = 0
        for name, playlist_type in _PLAYLIST_NAMES:
            color, color_text = _TYPE_COLORS[playlist_type]
            _, created = Playlist.objects.get_or_create(
                user=user,
                name=name,
                defaults={
                    "typePlaylist": playlist_type,
                    "color": color,
                    "colorText": color_text,
                    "volume": 75,
                    "is_copiable": True,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"{created_count}/{len(_PLAYLIST_NAMES)} playlists créées."
        ))
