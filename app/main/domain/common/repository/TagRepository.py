from typing import Any, Optional, List
from main.models.Tag import Tag


class TagRepository:

    def get_list_active_tags(self) -> List[Tag]:
        return Tag.objects.filter(is_active=True).order_by('name')