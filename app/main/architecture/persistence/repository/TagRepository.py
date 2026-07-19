from typing import Any, Optional, List
from main.architecture.persistence.models.SoundboardTag import SoundboardTag
from django.db.models import Count
from django.db import models
from django.db.models import QuerySet



class TagRepository:

    def get_with_uuid(self, uuid: str) -> Optional[SoundboardTag]:
        try:
            return SoundboardTag.objects.get(uuid=uuid)
        except SoundboardTag.DoesNotExist:
            return None

    def get_all_queryset(self, order_by: str = 'name') -> QuerySet[SoundboardTag]:
        return SoundboardTag.objects.all().order_by(order_by)

    def get_list_active_tags(self) -> List[SoundboardTag]:
        return SoundboardTag.objects.filter(is_active=True).order_by('name')
    
    def get_tag_with_count(self) -> List[SoundboardTag]:
        """
        Retourne la liste des tags avec le nombre de soundboard associés
        """
        tags = SoundboardTag.objects.filter(is_active=True).annotate(soundboard_count=models.Count('soundboards')).filter(soundboard_count__gt=0).order_by('-soundboard_count', 'name')
        return list(tags)