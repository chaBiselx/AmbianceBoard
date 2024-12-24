from ..models.Playlist import Playlist
from ..filters.PlaylistFilter import PlaylistFilter


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
        