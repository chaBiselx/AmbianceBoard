from typing import Any, Optional, List

from django.db.models import Avg, Count
from django.db import models
from django.db.models import QuerySet


from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.PlaylistDuplicationHistory import PlaylistDuplicationHistory
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.filters.PlaylistFilter import PlaylistFilter

class PlaylistRepository:

    def get(self, playlist_uuid) -> Optional[Playlist]:
        try:
            return Playlist.objects.get(uuid=playlist_uuid)
        except Playlist.DoesNotExist:
            return None
        
    def count_private(self, user: User) -> int:
        return Playlist.objects.filter(user=user).count()

    def get_listing_playlist(self, user:User, filter:dict) -> List[Playlist]:
        try:
            query_set = Playlist.objects.all()
            if 'typePlaylist' in filter:
                query_set = query_set.filter(typePlaylist=filter['typePlaylist'])
            return query_set.filter(user=user).order_by('updated_at') 
        except Exception:
            return []
        
    def count_private(self, user:User) -> int:
        return Playlist.objects.filter(user=user).count()

    def get_distinct_styles(self) -> List[str]:
        return Playlist.objects.values('colorText', 'color', 'typePlaylist').distinct().all()


    def get_stat_nb_track_per_playlist(self) -> int : 
        return Playlist.objects.annotate(
        music_count=models.Count('tracks')
        ).aggregate(avg_music=Avg('music_count'))['avg_music']
    
    def delete(self, playlist: Playlist) -> None:
        playlist.delete()
        
    def file_exists(self, file_path: str) -> bool:
        return Playlist.objects.filter(icon=file_path).exists()

    def get_all_queryset(self) -> QuerySet:
        return Playlist.objects.all()
    
    def get_default_volume_by_playlist(self, soundboard_uid: int):
        try:
            queryset = Playlist.objects.filter(soundboards__uuid=soundboard_uid).values('uuid', 'volume')
            result = {}
            for entry in queryset:
                result[str(entry['uuid'])] = {'volume':entry['volume']}
            return result
        except Exception:
            return []
    
    def get_copiable_playlists_excluding_user(self, user: User, filter:dict) -> List[Playlist]:
        """
        Récupère toutes les playlists copiables qui n'appartiennent pas à l'utilisateur.
        
        Args:
            user: L'utilisateur à exclure
            
        Returns:
            List[Playlist]: Liste des playlists copiables des autres utilisateurs
        """
        query_set = Playlist.objects.filter(
            is_copiable=True,
            moderator_ban_copie=False
        ).exclude(
            user=user
        ).select_related('user').order_by('-updated_at')
        if 'typePlaylist' in filter:
            query_set = query_set.filter(typePlaylist=filter['typePlaylist'])
        return query_set

    def get_copiable_playlists_for_soundboard(self, user: User, filter: dict) -> List[Playlist]:
        """
        Récupère les playlists copiables visibles en parcours public pour un soundboard cible.

        Règles appliquées:
        - playlist publique copiable et non bannie de copie
        - ne pas proposer les playlists du propriétaire du soundboard
        - exclure celles que l'utilisateur a déjà dupliquées (peu importe le soundboard cible),
          car PlaylistDuplicationService interdit la duplication multiple d'une même source
        """
        source_playlist_uuids_already_duplicated = PlaylistDuplicationHistory.objects.filter(
            duplicated_playlist__user=user
        ).values_list('source_playlist_uuid', flat=True)

        return self.get_copiable_playlists_excluding_user(user, filter).exclude(
            uuid__in=source_playlist_uuids_already_duplicated
        )

    def get_user_playlists_not_in_soundboard(self, user: User, soundboard: SoundBoard, filter: dict) -> List[Playlist]:
        """Récupère les playlists de l'utilisateur non encore intégrées dans le soundboard cible."""
        playlists_in_soundboard = SoundboardPlaylist.objects.filter(
            SoundBoard=soundboard
        ).values_list('Playlist_id', flat=True)

        query_set = Playlist.objects.filter(
            user=user,
            tracks__isnull=False,
        ).exclude(id__in=playlists_in_soundboard).distinct()
        if 'typePlaylist' in filter:
            query_set = query_set.filter(typePlaylist=filter['typePlaylist'])
        return query_set.order_by('name')
