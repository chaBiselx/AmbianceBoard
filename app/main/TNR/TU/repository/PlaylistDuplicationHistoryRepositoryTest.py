from django.test import TestCase, tag

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.PlaylistDuplicationHistory import PlaylistDuplicationHistory
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.PlaylistDuplicationHistoryRepository import PlaylistDuplicationHistoryRepository
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum


@tag('unitaire')
class PlaylistDuplicationHistoryRepositoryTest(TestCase):
    def setUp(self):
        self.repository = PlaylistDuplicationHistoryRepository()

        self.source_owner = User.objects.create_user(username='source', password='pw')  # NOSONAR
        self.target_user = User.objects.create_user(username='target', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', password='pw')  # NOSONAR

        self.source_playlist = Playlist.objects.create(
            user=self.source_owner,
            name='Source',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
        )

        self.duplicated_in_target_soundboard = Playlist.objects.create(
            user=self.target_user,
            name='Duplicated in target board',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=False,
        )
        self.duplicated_not_in_target_soundboard = Playlist.objects.create(
            user=self.target_user,
            name='Duplicated outside target board',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=False,
        )

        self.target_soundboard = SoundBoard.objects.create(user=self.target_user, name='Target board')
        self.other_soundboard = SoundBoard.objects.create(user=self.target_user, name='Other board')
        self.empty_soundboard = SoundBoard.objects.create(user=self.target_user, name='Empty board')

        SoundboardPlaylist.objects.create(
            SoundBoard=self.target_soundboard,
            Playlist=self.duplicated_in_target_soundboard,
            order=1,
        )
        SoundboardPlaylist.objects.create(
            SoundBoard=self.other_soundboard,
            Playlist=self.duplicated_not_in_target_soundboard,
            order=1,
        )

        self.history_in_target = PlaylistDuplicationHistory.objects.create(
            source_playlist=self.source_playlist,
            duplicated_playlist=self.duplicated_in_target_soundboard,
            source_playlist_name=self.source_playlist.name,
            source_playlist_uuid=self.source_playlist.uuid,
        )
        PlaylistDuplicationHistory.objects.create(
            source_playlist=self.source_playlist,
            duplicated_playlist=self.duplicated_not_in_target_soundboard,
            source_playlist_name=self.source_playlist.name,
            source_playlist_uuid=self.source_playlist.uuid,
        )

    def test_find_existing_duplication_in_soundboard_returns_history_when_present(self):
        history = self.repository.find_existing_duplication_in_soundboard(
            source_playlist_uuid=self.source_playlist.uuid,
            target_user=self.target_user,
            target_soundboard=self.target_soundboard,
        )

        self.assertIsNotNone(history)
        self.assertEqual(history.id, self.history_in_target.id)

    def test_find_existing_duplication_in_soundboard_returns_none_when_source_not_in_soundboard(self):
        history = self.repository.find_existing_duplication_in_soundboard(
            source_playlist_uuid=self.source_playlist.uuid,
            target_user=self.target_user,
            target_soundboard=self.empty_soundboard,
        )

        self.assertIsNone(history)

    def test_find_existing_duplication_in_soundboard_returns_none_for_other_user(self):
        history = self.repository.find_existing_duplication_in_soundboard(
            source_playlist_uuid=self.source_playlist.uuid,
            target_user=self.other_user,
            target_soundboard=self.target_soundboard,
        )

        self.assertIsNone(history)
