from django.contrib import messages
from home.enum.PermissionEnum import PermissionEnum
from parameters import settings
from home.models.Playlist import Playlist
from home.filters.PlaylistFilter import PlaylistFilter
from home.forms.PlaylistForm import PlaylistForm



class PlaylistService:
    
    def __init__(self, request):
        self.request = request
    
    def get_playlist(self, playlist_id:int)-> Playlist|None :
        try:
            playlist = Playlist.objects.get(id=playlist_id)
            if not playlist or playlist.user != self.request.user:
                return None

            return playlist
        except Playlist.DoesNotExist:
            return None
        
    def get_all_playlist(self)-> list[Playlist] :
        try:
            _query_set = Playlist.objects.all().order_by('id')
            _filter = PlaylistFilter(queryset=_query_set)
            playlists = _filter.filter_by_user(self.request.user)
        except Exception:
            playlists = []
        return playlists
    
    def save_form(self):
        if(self.request.user.has_perm('auth.' + PermissionEnum.USER_PREMIUM_OVER_LIMIT_PLAYLIST.name)):  
            limit_playlist = settings.LIMIT_USER_PREMIUM_PLAYLIST
        else:
            limit_playlist = settings.LIMIT_USER_STANDARD_PLAYLIST
        
        if len(Playlist.objects.filter(user=self.request.user)) >= limit_playlist:
            messages.error(self.request, "Vous avez atteint la limite de playlist total (" + str(limit_playlist) + ").")
            return None
        
        form = PlaylistForm(self.request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = self.request.user
            playlist.save()
            return playlist
        else:
            for(field, errors) in form.errors.items():
                for error in errors:
                    messages.error(self.request, error)
        return None
        