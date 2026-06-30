from django.test import TestCase, tag

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.PlaylistDuplicationHistory import PlaylistDuplicationHistory
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.PlaylistRepository import PlaylistRepository
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum


@tag('unitaire')
class PlaylistRepositoryTest(TestCase):
    def setUp(self):
        self.repository = PlaylistRepository()

        self.owner = User.objects.create_user(username='owner', password='pw')  # NOSONAR
        self.target_user = User.objects.create_user(username='target', password='pw')  # NOSONAR

        self.soundboard = SoundBoard.objects.create(user=self.owner, name='Board')

        self.playlist_music = Playlist.objects.create(
            user=self.owner,
            name='Music Copiable',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
            moderator_ban_copie=False,
        )
        self.playlist_ambient = Playlist.objects.create(
            user=self.owner,
            name='Ambient Copiable',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name,
            is_copiable=True,
            moderator_ban_copie=False,
        )
        self.playlist_not_copiable = Playlist.objects.create(
            user=self.owner,
            name='Not Copiable',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=False,
            moderator_ban_copie=False,
        )
        self.playlist_banned = Playlist.objects.create(
            user=self.owner,
            name='Banned',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
            moderator_ban_copie=True,
        )
        self.playlist_owned_by_target = Playlist.objects.create(
            user=self.target_user,
            name='Owned by target',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
            moderator_ban_copie=False,
        )

    def test_get_copiable_playlists_excluding_user_filters_non_copiable_banned_and_user_owned(self):
        result = self.repository.get_copiable_playlists_excluding_user(self.target_user, {})
        result_ids = {playlist.id for playlist in result}

        self.assertIn(self.playlist_music.id, result_ids)
        self.assertIn(self.playlist_ambient.id, result_ids)
        self.assertNotIn(self.playlist_not_copiable.id, result_ids)
        self.assertNotIn(self.playlist_banned.id, result_ids)
        self.assertNotIn(self.playlist_owned_by_target.id, result_ids)

    def test_get_copiable_playlists_excluding_user_applies_type_filter(self):
        result = self.repository.get_copiable_playlists_excluding_user(
            self.target_user,
            {'typePlaylist': PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name},
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, self.playlist_ambient.id)

    def test_get_copiable_playlists_for_soundboard_excludes_sources_already_duplicated_by_user(self):
        duplicated_playlist = Playlist.objects.create(
            user=self.target_user,
            name='Already duplicated playlist',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=False,
        )

        PlaylistDuplicationHistory.objects.create(
            source_playlist=self.playlist_music,
            duplicated_playlist=duplicated_playlist,
            source_playlist_name=self.playlist_music.name,
            source_playlist_uuid=self.playlist_music.uuid,
        )

        result = self.repository.get_copiable_playlists_for_soundboard(
            self.target_user,
            {},
        )
        result_ids = {playlist.id for playlist in result}

        self.assertNotIn(self.playlist_music.id, result_ids)
        self.assertIn(self.playlist_ambient.id, result_ids)
