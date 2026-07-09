from typing import Optional, List
from django.db import models
from django.db.models import QuerySet
from main.architecture.persistence.models.PlaylistTag import PlaylistTag


class PlaylistTagRepository:

    def get_with_label(self, label: str) -> Optional[PlaylistTag]:
        try:
            return PlaylistTag.objects.get(label=label)
        except PlaylistTag.DoesNotExist:
            return None

    def get_all_queryset(self, order_by: str = "name") -> QuerySet[PlaylistTag]:
        return PlaylistTag.objects.all().order_by(order_by)

    def get_list_active_tags(self) -> List[PlaylistTag]:
        return PlaylistTag.objects.filter(is_active=True).order_by("name")

    def get_tag_with_count(self) -> List[PlaylistTag]:
        tags = (
            PlaylistTag.objects.filter(is_active=True)
            .annotate(playlist_count=models.Count("playlists"))
            .filter(playlist_count__gt=0)
            .order_by("-playlist_count", "name")
        )
        return list(tags)
