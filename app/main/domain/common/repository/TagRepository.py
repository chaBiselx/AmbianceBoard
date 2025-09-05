from typing import Any, Optional, List
from main.architecture.persistence.models.Tag import Tag
from django.db.models import Count
from django.db import models



class TagRepository:

    def get_with_uuid(self, uuid: str) -> Optional[Tag]:
        try:
            return Tag.objects.get(uuid=uuid)
        except Tag.DoesNotExist:
            return None

    def get_all_queryset(self, order_by: str = 'name') -> models.QuerySet[Tag]:
        return Tag.objects.all().order_by(order_by)

    def get_list_active_tags(self) -> List[Tag]:
        return Tag.objects.filter(is_active=True).order_by('name')
    
    def get_tag_with_count(self) -> List[Tag]:
        """
        Retourne la liste des tags avec le nombre de soundboard associés
        """
        tags = Tag.objects.filter(is_active=True).annotate(soundboard_count=models.Count('soundboards')).filter(soundboard_count__gt=0).order_by('-soundboard_count', 'name')
        return list(tags)