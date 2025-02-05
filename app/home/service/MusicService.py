import uuid
from django.contrib import messages
from home.enum.PermissionEnum import PermissionEnum
from home.models.Playlist import Playlist
from home.models.Music import Music
from home.filters.MusicFilter import MusicFilter
from home.forms.MusicForm import MusicForm
from home.factory.UserParametersFactory import UserParametersFactory
from home.service.SoundBoardService import SoundBoardService


class MusicService:
    
    def __init__(self, request):
        self.request = request
    
    def get_random_music(self, playlist_id:int)-> Music|None :
        try:
            music_filter = MusicFilter()
            music_filter.filter_by_user(self.request.user)
            return self._get_random_music_from_playlist(music_filter, playlist_id)
        except Playlist.DoesNotExist:
            return None
    
    def get_public_random_music(self, soundboard_id:uuid, playlist_id:int)-> Music|None :
        soundboard = (SoundBoardService(self.request)).get_public_soundboard(soundboard_id)
        if not soundboard:
            return None
        try:
            music_filter = MusicFilter()
            return self._get_random_music_from_playlist(music_filter, playlist_id)
        except Playlist.DoesNotExist:
            return None
        
    def _get_random_music_from_playlist(self, music_filter:MusicFilter, playlist_id:int)-> Music|None :
        queryset = music_filter.filter_by_playlist(playlist_id)
        return queryset.order_by('?').first()
        
        
    def get_list_music(self, playlist_id:int)-> list[Music]|None :
        try:
            music_filter = MusicFilter()
            queryset = music_filter.filter_by_user(self.request.user)
            queryset = music_filter.filter_by_playlist(playlist_id)
            return queryset
        except Playlist.DoesNotExist:
            return None
        
    def save_form(self, playlist:Playlist):
        user_parameters = UserParametersFactory(self.request.user)
        limit_music_per_playlist = user_parameters.limit_music_per_playlist
            
        if(len(Music.objects.filter(playlist=playlist)) >= limit_music_per_playlist):
            messages.error(self.request, "Vous avez atteint la limite de musique par playlist (" + str(limit_music_per_playlist) + " max).")
            return None
            
        form = MusicForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            limit_weight_file = user_parameters.limit_weight_file
            
            if(form.cleaned_data['file'].size > limit_weight_file*1024*1024):
                messages.error(self.request, "Le poids du fichier est trop lourd (" + str(limit_weight_file) + "Mo max).")
                return None
            
            music = form.save(commit=False)
            music.playlist = playlist
            music.save()
            return music
        else :
            for(field, errors) in form.errors.items():
                for error in errors:
                    messages.error(self.request, error)
        return None
        

        