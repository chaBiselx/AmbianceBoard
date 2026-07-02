from typing import List
from main.architecture.persistence.models.HomeDemoItem import HomeDemoItem
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.repository.SoundBoardRepository import SoundBoardRepository
from main.architecture.persistence.repository.TagRepository import TagRepository


class HomeDemoItemRepository:

    def get_all_items(self) -> List[HomeDemoItem]:
        return HomeDemoItem.objects.select_related('soundboard').all().order_by('-updated_at')

    def get_used_soundboard_ids(self) -> list[int]:
        return list(
            HomeDemoItem.objects.filter(is_active=True)
            .values_list('soundboard_id', flat=True)
            .distinct()
        )

    def get_selectable_public_queryset(self, selected_tag: str | None = None):
        queryset = SoundBoardRepository().get_search_public_queryset(selected_tag)
        used_soundboard_ids = self.get_used_soundboard_ids()
        if used_soundboard_ids:
            queryset = queryset.exclude(id__in=used_soundboard_ids)
        return queryset

    def get_active_random_items(self, limit: int = 4) -> List[HomeDemoItem]:
        return list(
            HomeDemoItem.objects.select_related('soundboard')
            .filter(is_active=True, soundboard__is_public=True)
            .order_by('?')[:limit]
        )

    def get_item_by_uuid(self, uuid: str) -> HomeDemoItem | None:
        try:
            return HomeDemoItem.objects.get(uuid=uuid)
        except HomeDemoItem.DoesNotExist:
            return None
