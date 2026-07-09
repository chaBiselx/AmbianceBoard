from django.test import TestCase, tag

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardTag import SoundboardTag
from main.architecture.persistence.models.Track import Track
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.SoundBoardRepository import SoundBoardRepository
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum


@tag('unitaire')
class SoundBoardRepositoryTest(TestCase):
    def setUp(self):
        self.repository = SoundBoardRepository()

        self.allowed_user = User.objects.create_user(username='allowed-user', password='pw')  # NOSONAR
        self.banned_user = User.objects.create_user(username='banned-user', password='pw', isBan=True)  # NOSONAR

        self.tag_horror = SoundboardTag.objects.create(name='horror')

        self.playlist_with_track = Playlist.objects.create(
            user=self.allowed_user,
            name='Playlist with track',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )
        Track.objects.create(
            playlist=self.playlist_with_track,
            alternativeName='track-1',
        )

        self.playlist_without_track = Playlist.objects.create(
            user=self.allowed_user,
            name='Playlist without track',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )

        self.public_with_track = SoundBoard.objects.create(
            user=self.allowed_user,
            name='Public with track',
            is_public=True,
        )
        self.public_with_track.playlists.add(self.playlist_with_track)
        self.public_with_track.tags.add(self.tag_horror)

        self.public_without_track = SoundBoard.objects.create(
            user=self.allowed_user,
            name='Public without track',
            is_public=True,
        )
        self.public_without_track.playlists.add(self.playlist_without_track)

        self.private_with_track = SoundBoard.objects.create(
            user=self.allowed_user,
            name='Private with track',
            is_public=False,
        )
        self.private_with_track.playlists.add(self.playlist_with_track)

        banned_playlist = Playlist.objects.create(
            user=self.banned_user,
            name='Banned playlist',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )
        Track.objects.create(
            playlist=banned_playlist,
            alternativeName='banned-track',
        )
        self.banned_public_with_track = SoundBoard.objects.create(
            user=self.banned_user,
            name='Banned public with track',
            is_public=True,
        )
        self.banned_public_with_track.playlists.add(banned_playlist)

    def test_get_search_public_queryset_returns_only_public_not_banned_with_tracks(self):
        result = self.repository.get_search_public_queryset()
        result_ids = {soundboard.id for soundboard in result}

        self.assertIn(self.public_with_track.id, result_ids)
        self.assertNotIn(self.public_without_track.id, result_ids)
        self.assertNotIn(self.private_with_track.id, result_ids)
        self.assertNotIn(self.banned_public_with_track.id, result_ids)

    def test_get_search_public_queryset_with_selected_tag_filters_result(self):
        result = self.repository.get_search_public_queryset(selected_tag='horror')
        result_ids = {soundboard.id for soundboard in result}

        self.assertIn(self.public_with_track.id, result_ids)
        self.assertNotIn(self.public_without_track.id, result_ids)
