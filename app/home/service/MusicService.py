from django.contrib import messages
from home.enum.PermissionEnum import PermissionEnum
from parameters import settings
from home.models.Playlist import Playlist
from home.models.Music import Music
from home.filters.MusicFilter import MusicFilter
from home.forms.MusicForm import MusicForm


class MusicService:
    
    def __init__(self, request):
        self.request = request
    
    def get_random_music(self, playlist_id:int)-> Music|None :
        try:
            music_filter = MusicFilter()
            queryset = music_filter.filter_by_user(self.request.user)
            queryset = music_filter.filter_by_playlist(playlist_id)
            return queryset.order_by('?').first()
        except Playlist.DoesNotExist:
            return None
        
    def get_list_music(self, playlist_id:int)-> list[Music]|None :
        try:
            music_filter = MusicFilter()
            queryset = music_filter.filter_by_user(self.request.user)
            queryset = music_filter.filter_by_playlist(playlist_id)
            return queryset
        except Playlist.DoesNotExist:
            return None
        
    def save_form(self, playlist:Playlist):
        if(self.request.user.has_perm('auth.' + PermissionEnum.USER_PREMIUM_OVER_LIMIT_SOUNDBOARD.name)):  
            limit_music_per_playlist = settings.LIMIT_USER_PREMIUM_MUSIC_PER_PLAYLIST
        else:
            limit_music_per_playlist = settings.LIMIT_USER_STANDARD_MUSIC_PER_PLAYLIST
            
        if(len(Music.objects.filter(playlist=playlist)) >= limit_music_per_playlist):
            messages.error(self.request, "Vous avez atteint la limite de musique par playlist (" + str(limit_music_per_playlist) + " max).")
            return None
            
        form = MusicForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            if(self.request.user.has_perm('auth.' + PermissionEnum.USER_PREMIUM_OVER_LIMIT_MUSIC_PER_PLAYLIST.name)):  
                limit_weight_file = settings.LIMIT_USER_PREMIUM_WEIGHT_MUSIC
            else:
                limit_weight_file = settings.LIMIT_USER_STANDARD_WEIGHT_MUSIC
            
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
        

        