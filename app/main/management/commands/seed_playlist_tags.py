from django.core.management.base import BaseCommand
from django.db import transaction

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.PlaylistTag import PlaylistTag


PLAYLIST_TAGS = (
    {"label": "combat", "name": "combat", "description": "Playlists for combat scenes"},
    {"label": "tension", "name": "tension", "description": "Playlists for suspense and tension"},
    {"label": "exploration", "name": "exploration", "description": "Playlists for travel and discovery"},
    {"label": "ville", "name": "ville", "description": "Playlists for city and social scenes"},
    {"label": "mystere", "name": "mystere", "description": "Playlists for mystery scenes"},
)

TAGS_BY_PLAYLIST_TYPE = {
    "PLAYLIST_TYPE_INSTANT": ("combat", "tension"),
    "PLAYLIST_TYPE_AMBIENT": ("exploration", "ville", "mystere"),
    "PLAYLIST_TYPE_MUSIC": ("combat", "mystere"),
}


class Command(BaseCommand):
    help = "Seed playlist tags and assign them to playlists (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default=None,
            help="Optional username to restrict playlist assignment.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Maximum number of playlists to process.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options.get("username")
        limit = max(0, int(options.get("limit") or 0))

        created_tags = 0
        tag_by_name = {}
        for payload in PLAYLIST_TAGS:
            playlist_tag, created = PlaylistTag.objects.get_or_create(
                label=payload["label"],
                defaults={
                    "name": payload["name"],
                    "description": payload["description"],
                    "is_active": True,
                },
            )
            if created:
                created_tags += 1
            tag_by_name[playlist_tag.name] = playlist_tag

        queryset = Playlist.objects.all().order_by("id")
        if username:
            queryset = queryset.filter(user__username=username)
        if limit > 0:
            queryset = queryset[:limit]

        processed_playlists = 0
        assignments_created = 0

        for playlist in queryset:
            processed_playlists += 1
            names = TAGS_BY_PLAYLIST_TYPE.get(playlist.typePlaylist, ())
            tags = [tag_by_name[name] for name in names if name in tag_by_name]
            before_count = playlist.playlist_tags.count()
            if tags:
                playlist.playlist_tags.add(*tags)
            after_count = playlist.playlist_tags.count()
            assignments_created += max(0, after_count - before_count)

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "seed_playlist_tags done: "
                    f"created_tags={created_tags} "
                    f"processed_playlists={processed_playlists} "
                    f"new_assignments={assignments_created}"
                )
            )
        )
