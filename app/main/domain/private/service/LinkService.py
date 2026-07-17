from typing import Optional
from django.http import HttpRequest
from main.architecture.persistence.models.LinkMusic import LinkMusic
from main.architecture.persistence.models.Playlist import Playlist
from main.interface.ui.forms.private.LinkMusicForm import LinkMusicForm
from main.domain.brokers.message.YoutubeAudioDownloadMessenger import download_youtube_audio
from main.domain.common.factory.UserParametersFactory import UserParametersFactory
from main.architecture.persistence.repository.TrackRepository import TrackRepository
from main.domain.common.exceptions.PlaylistLimitException import PlaylistLimitException


class LinkService:
    
    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        self.link_type = "default"
        self.track_repository = TrackRepository()

    
    def save_form(self, playlist: Playlist, link: Optional[LinkMusic] = None) -> LinkMusic|None:
        """Sauvegarde un formulaire de lien musical"""
        form = LinkMusicForm(self.request.POST, instance=link)
        
        if form.is_valid():
            # detection du type de lien
            if self.__is_youtube_link(form.cleaned_data.get('url', '')):
                
                self.link_type = "youtube"
                self.__controle_limit_user_berfore_download(playlist)
                self.__handle_youtube_link(playlist, form)
                return None
                
            
            link_music = form.save(commit=False)
            link_music.playlist = playlist
            link_music.save()
            return link_music
        else:
            # Lever une exception avec les erreurs du formulaire
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            raise ValueError("; ".join(error_messages))
        
    def get_success_message(self) -> str:
        """Retourne le message de succès après l'ajout d'un lien musical"""
        if(self.link_type == "youtube"):
            return "La piste youtube sera intégrée prochainement!"
        return "Lien musical ajouté avec succès!"
    
    def __is_youtube_link(self, url: str) -> bool:
        """Vérifie si l'URL est un lien YouTube"""
        return "youtube.com" in url or "youtu.be" in url
    
    def __handle_youtube_link(self, playlist: Playlist, form: LinkMusicForm) -> None:
        """Gère le cas où le lien est un lien YouTube"""
        download_youtube_audio.apply_async(
            args=[str(playlist.uuid), form.cleaned_data['url'], self.request.user.id, form.cleaned_data.get('alternativeName', None)],
            queue='default',
            priority=1,
        )
        
    def __controle_limit_user_berfore_download(self, playlist: Playlist) -> None:
        """Contrôle la limite d'ajout de liens YouTube pour l'utilisateur"""
        user = self.request.user
        if user.is_authenticated:
            user_parameters = UserParametersFactory(self.request.user)
            limit_music_per_playlist = user_parameters.limit_music_per_playlist
            
            nbFinal = self.track_repository.get_count(playlist) + 0 # TODO a BDD pour compter les liens youtube en cours de téléchargement
            if nbFinal >= limit_music_per_playlist:
                raise PlaylistLimitException(f"Vous avez atteint la limite de {limit_music_per_playlist} musiques par playlist.")
