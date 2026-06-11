from typing import Any, Optional, List
from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.filters.MusicFilter import MusicFilter


class MusicRepository:

    def get_music(self, id_music:int) -> Music|None:
        try:
            return Music.objects.get(id=id_music)
        except Music.DoesNotExist:
            return None

    def exist_from_path(self, file_path: str) -> bool:
        return Music.objects.filter(file=file_path).exists()

    def is_file_used_elsewhere(self, file, music_id: int) -> bool:
        """
        Vérifie si un fichier musique est encore référencé par une autre entrée.

        Args:
            file: Chemin du fichier ou objet `FieldFile`.
            music_id: Identifiant de la musique courante à exclure.

        Returns:
            bool: True si au moins une autre musique utilise ce fichier.
        """
        if not file:
            return False

        file_name = getattr(file, 'name', file)
        return Music.objects.filter(file=file_name).exclude(id=music_id).exists()
    
    def get_list_music(self, playlist_uuid: int, user:User) -> Optional[List[Music]]:
        try:
            music_filter = MusicFilter() 
            queryset = music_filter.filter_by_user(user)
            queryset = music_filter.filter_by_playlist(playlist_uuid)
            return queryset
        except Music.DoesNotExist:
            return None

    def get_unlabeled_music_ids(self, limit: int = 50) -> list[int]:
        """
        Retourne les IDs des musiques sans labels.
        Sélection des plus anciennes limitées à `limit`.
        """
        return list(
            Music.objects
            .filter(file__isnull=False, labels__isnull=True)
            .order_by('created_at')
            .values_list('track_ptr_id', flat=True)[:limit]
        )

