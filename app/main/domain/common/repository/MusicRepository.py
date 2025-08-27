from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.User import User
from main.domain.common.repository.filters.MusicFilter import MusicFilter

class MusicRepository:

    def get_music(self, id_music:int) -> Music|None:
        return Music.objects.get(id=id_music)

    def exist_from_path(self, file_path: str) -> bool:
        return Music.objects.filter(file=file_path).exists()

