from django.core.management.base import BaseCommand
from django.db import transaction

from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardTag import SoundboardTag


SOUNDBOARD_TAGS = (
    {"name": "cyberpunk", "description": "soundboard for cyberpunk scenes"},
    {"name": "dark_fantasy", "description": "soundboard for dark fantasy scenes"},
    {"name": "pirate", "description": "soundboard for pirate scenes"},
    {"name": "onirique", "description": "soundboard for dreamlike scenes"},
    {"name": "horror", "description": "soundboard for horror scenes"},
)




class Command(BaseCommand):
    help = "Seed soundboard tags and assign them to soundboards (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default=None,
            help="Optional username to restrict soundboard assignment.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Maximum number of soundboards to process.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options.get("username")
        limit = max(0, int(options.get("limit") or 0))

        created_tags = 0
        tag_by_name = {}
        for payload in SOUNDBOARD_TAGS:
            soundboard_tag, created = SoundboardTag.objects.get_or_create(
                name=payload["name"],
                defaults={
                    "description": payload["description"],
                    "is_active": True,
                },
            )
            if created:
                created_tags += 1
            tag_by_name[soundboard_tag.name] = soundboard_tag

        queryset = SoundBoard.objects.all().order_by("id")
        if username:
            queryset = queryset.filter(user__username=username)
        if limit > 0:
            queryset = queryset[:limit]

        processed_soundboard = 0
        assignments_created = 0
        default_tags = list(tag_by_name.values())

        for soundboard in queryset:
            processed_soundboard += 1
            # No type field exists on SoundBoard in current schema, so assign
            # the seeded tags set to each soundboard.
            tags = default_tags
            before_count = soundboard.tags.count()
            if tags:
                soundboard.tags.add(*tags)
            after_count = soundboard.tags.count()
            assignments_created += max(0, after_count - before_count)

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "seed_soundboard_tags done: "
                    f"created_tags={created_tags} "
                    f"processed_soundboard={processed_soundboard} "
                    f"new_assignments={assignments_created}"
                )
            )
        )
