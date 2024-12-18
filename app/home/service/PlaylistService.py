from ..models.Playlist import Playlist


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
        
        