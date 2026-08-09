from typing import Any, Optional, List
from main.architecture.persistence.models.SoundboardTag import SoundboardTag
from django.db.models import Count
from django.db import models
from django.db.models import QuerySet



class SoundboardTagRepository:
    
    def create(self, name: str, description: str = "", is_active: bool = True, is_default: bool = False) -> SoundboardTag:
        """
        Crée un nouveau tag de soundboard.
        """
        tag = SoundboardTag(name=name, description=description, is_active=is_active, is_default=is_default)
        tag.save()
        return tag

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
    
    def get_default_tag(self) -> Optional[SoundboardTag]:
        """
        Retourne le tag par défaut s'il existe
        """
        try:
            return SoundboardTag.objects.get(is_default=True)
        except SoundboardTag.DoesNotExist:
            try:
                return SoundboardTag.objects.filter(is_active=True).first()  # Retourne le premier tag actif s'il n'y a pas de tag par défaut
            except SoundboardTag.DoesNotExist:
                return self.create(name="Default", description="Tag par défaut créé automatiquement", is_active=True, is_default=True)