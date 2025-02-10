import logging
from ..models.SoundBoard import SoundBoard
from ..models.Playlist import Playlist
from ..service.PlaylistService import PlaylistService

class SoundBoardPlaylistManager:
    def __init__(self, request, soundboard: SoundBoard):
        self.request = request
        self.soundboard = soundboard

    def get_playlists(self):
        return list(self.soundboard.playlists.all().order_by('soundboard_playlist__order'))

    def get_unassociated_playlists(self):
        all_playlists = list((PlaylistService(self.request)).get_all_playlist())
        associated_playlists = list(self.soundboard.playlists.all())
        return [playlist for playlist in all_playlists if playlist not in associated_playlists]