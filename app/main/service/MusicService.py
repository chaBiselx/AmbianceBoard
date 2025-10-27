import uuid
from typing import Optional, List
from django.http import HttpRequest
from django.core.files.uploadedfile import UploadedFile
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.Music import Music
from main.interface.ui.forms.private.MusicForm import MusicForm
from main.domain.common.factory.UserParametersFactory import UserParametersFactory
from main.service.SoundBoardService import SoundBoardService
from main.domain.common.enum.MusicFormatEnum import MusicFormatEnum
from main.architecture.persistence.repository.TrackRepository import TrackRepository


class MusicService:
    
    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        self.track_repository = TrackRepository()

    def get_specific_music(self, playlist_uuid: int, music_id: int) -> Optional[Music]:
        """        Récupère une musique spécifique par son ID dans une playlist.
        Args:
            playlist_uuid (int): L'UUID de la playlist.
            music_id (int): L'ID de la musique à récupérer.
        """
        return self.track_repository.get(music_id=music_id, playlist_uuid=playlist_uuid)    
    
        
    def save_form(self, playlist: Playlist, music: Optional[Music] = None) -> Optional[Music]:
        user_parameters = UserParametersFactory(self.request.user)
        limit_music_per_playlist = user_parameters.limit_music_per_playlist

        if(self.track_repository.get_count(playlist) >= limit_music_per_playlist):
            raise ValueError("Vous avez atteint la limite de musique par playlist (" + str(limit_music_per_playlist) + " max).")
            
        form = MusicForm(self.request.POST, self.request.FILES, instance=music)
        if form.is_valid():
            limit_weight_file = user_parameters.limit_weight_file
            
            if(form.cleaned_data['file'].size > limit_weight_file*1024*1024):
                raise ValueError("Le poids du fichier est trop lourd.")
            
            music = form.save(commit=False)
            music.playlist = playlist
            music.save()
            return music
        else :
            for(field, errors) in form.errors.items():
                for error in errors:
                    raise ValueError("Erreur dans le formulaire: " + error)
        return None
    
    def save_multiple_files_item(self, playlist: Playlist, file: UploadedFile) -> Music:
        """Sauvegarde un fichier individuel dans le contexte d'un upload multiple"""
        user_parameters = UserParametersFactory(self.request.user)
        limit_music_per_playlist = user_parameters.limit_music_per_playlist

        # Vérifier la limite de musiques par playlist
        if self.track_repository.get_count(playlist) >= limit_music_per_playlist:
            raise ValueError("Vous avez atteint la limite de musique par playlist (" + str(limit_music_per_playlist) + " max).")
        
        # Vérifier le poids du fichier
        limit_weight_file = user_parameters.limit_weight_file
        if file.size > limit_weight_file * 1024 * 1024:
            raise ValueError("Le poids du fichier est trop lourd.")
        
        # Vérifier l'extension du fichier
        allowed_extensions = MusicFormatEnum.values()  # Convert enum values to list
        if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f"Seuls les fichiers audio ({', '.join(allowed_extensions)}) sont autorisés.")

        # Créer l'objet Music
        music = Music()
        music.file = file
        music.alternativeName = file.name.split('.')[0][0:63]
        music.playlist = playlist
        music.save()
        
        return music
