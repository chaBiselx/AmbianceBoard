from django.core.exceptions import FieldError
from django.test import TestCase, tag

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.filters.PlaylistFilter import PlaylistFilter
from main.architecture.persistence.repository.filters.SoundBoardFilter import SoundBoardFilter
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum


@tag('unitaire')
class RepositoryFiltersTest(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='filter-user-a', password='pw')
        self.user_b = User.objects.create_user(username='filter-user-b', password='pw')

        self.playlist = Playlist.objects.create(
            user=self.user_a,
            name='Filter playlist',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )

        self.soundboard_a = SoundBoard.objects.create(user=self.user_a, name='SB A')
        self.soundboard_b = SoundBoard.objects.create(user=self.user_b, name='SB B')

    def test_playlist_filter_uses_default_queryset_when_no_argument(self):
        playlist_filter = PlaylistFilter()

        result = list(playlist_filter.filter_by_playlist(None))

        self.assertTrue(any(p.id == self.playlist.id for p in result))

    def test_playlist_filter_by_playlist_raises_field_error_due_to_invalid_field_name(self):
        playlist_filter = PlaylistFilter()

        with self.assertRaises(FieldError):
            list(playlist_filter.filter_by_playlist(self.playlist.id))

    def test_soundboard_filter_uses_default_queryset_when_user_missing(self):
        soundboard_filter = SoundBoardFilter()

        result = list(soundboard_filter.filter_by_user(None))
        result_ids = {sb.id for sb in result}

        self.assertIn(self.soundboard_a.id, result_ids)
        self.assertIn(self.soundboard_b.id, result_ids)

    def test_soundboard_filter_filters_by_user(self):
        soundboard_filter = SoundBoardFilter()

        result = list(soundboard_filter.filter_by_user(self.user_a))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.soundboard_a.id)
