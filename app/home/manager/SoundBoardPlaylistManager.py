from ..models.SoundBoard import SoundBoard
from ..models.Playlist import Playlist
from ..service.PlaylistService import PlaylistService

class SoundBoardPlaylistManager:
    def __init__(self, request, soundboard: SoundBoard):
        self.request = request
        self.soundboard = soundboard

    def get_playlists(self):
        return (PlaylistService(self.request)).get_all_playlist()

    def get_unassociated_playlists(self):
        all_playlists = self.get_playlists()
        associated_playlists = self.soundboard.playlists.all()
        return [playlist for playlist in all_playlists if playlist not in associated_playlists]