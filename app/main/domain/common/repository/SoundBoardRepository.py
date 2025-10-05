from typing import Any, Optional, List
from django.db.models import QuerySet

from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.domain.common.repository.filters.SoundBoardFilter import SoundBoardFilter


class SoundBoardRepository:

    def get_list_from_user(self, user: User, order: str = 'uuid') -> List[SoundBoard]:
        _query_set = SoundBoard.objects.all().order_by(order)
        _filter = SoundBoardFilter(queryset=_query_set)
        soundboards = _filter.filter_by_user(user)
        return soundboards

    def get(self, soundboard_uid: str) -> Optional[SoundBoard]:
        try:
            return SoundBoard.objects.get(uuid=soundboard_uid)
        except SoundBoard.DoesNotExist:
            return None
        
    def count_private(self, user: User) -> int:
        return SoundBoard.objects.filter(user=user).count()
    
    def get_count_with_user(self, user: User) -> int:
        return SoundBoard.objects.filter(user=user).count()

    def get_search_public_queryset(self, selected_tag: Optional[str] = None) -> QuerySet[SoundBoard]:
        queryset = SoundBoard.objects.filter(is_public=True, user__isBan=False)
        if selected_tag:
            queryset = queryset.filter(tags__name=selected_tag)
        
        return queryset.order_by('uuid')
    
    def get_favorite_public_queryset(self, user: User) -> QuerySet[SoundBoard]:
        return  SoundBoard.objects.filter(
            favorite__user=user,
            is_public=True, 
            user__isBan=False
        ).order_by('uuid')
        


