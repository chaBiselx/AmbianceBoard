from django.test import TestCase, tag

from main.architecture.persistence.models.PlaylistColorUser import PlaylistColorUser
from main.architecture.persistence.models.User import User
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.service.DefaultColorPlaylistService import DefaultColorPlaylistService
from main.domain.common.utils.cache.CacheFactory import CacheFactory


@tag('unitaire')
class DefaultColorPlaylistServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='default-color-user', password='pw')
        self.service = DefaultColorPlaylistService(self.user)
        self.cache = CacheFactory.get_default_cache()
        for playlist_type in PlaylistTypeEnum:
            self.cache.delete(f"default_color:{self.user.id}:{playlist_type.name}")
            self.cache.delete(f"default_color_text:{self.user.id}:{playlist_type.name}")

    def test_get_list_default_color_returns_default_values_for_each_playlist_type(self):
        result = self.service.get_list_default_color()

        self.assertEqual(len(result), len(PlaylistTypeEnum))
        self.assertEqual(result[0]['typePlaylist'], PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name)
        self.assertEqual(result[0]['color'], PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.get_default_color()['color'])
        self.assertEqual(result[0]['colorText'], PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.get_default_color()['colorText'])

    def test_get_list_default_color_ajax_uses_enum_values_and_custom_colors(self):
        PlaylistColorUser.objects.create(
            user=self.user,
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            color='#112233',
            colorText='#aabbcc',
        )

        result = self.service.get_list_default_color_ajax()
        music_entry = next(item for item in result if item['typePlaylist'] == PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.value)

        self.assertEqual(music_entry['color'], '#112233')
        self.assertEqual(music_entry['colorText'], '#aabbcc')
        self.assertEqual(
            [item['typePlaylist'] for item in result],
            [playlist_type.value for playlist_type in PlaylistTypeEnum],
        )

    def test_get_default_color_and_text_use_user_overrides(self):
        PlaylistColorUser.objects.create(
            user=self.user,
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name,
            color='#654321',
            colorText='#fedcba',
        )

        self.assertEqual(
            self.service.get_default_color(PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name),
            '#654321',
        )
        self.assertEqual(
            self.service.get_default_color_text(PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name),
            '#fedcba',
        )

    def test_get_list_playlist_enum_with_color_returns_enum_members_with_colors(self):
        result = self.service.get_list_playlist_enum_with_color()

        self.assertEqual([item['typePlaylist'] for item in result], list(PlaylistTypeEnum))
        self.assertEqual(
            result[1]['color'],
            PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.get_default_color()['color'],
        )
        self.assertEqual(
            result[1]['colorText'],
            PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.get_default_color()['colorText'],
        )
