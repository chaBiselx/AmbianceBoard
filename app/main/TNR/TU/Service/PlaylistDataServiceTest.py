"""
Tests unitaires pour le service PlaylistDataService.
"""

from types import SimpleNamespace
from uuid import uuid4
from django.test import SimpleTestCase, tag

from main.domain.common.enum.FadeEnum import FadeEnum
from main.domain.common.enum.FadePlaylistEnum import FadePlaylistEnum
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.service.PlaylistDataService import PlaylistDataService


@tag('unitaire')
class PlaylistDataServiceTest(SimpleTestCase):
    """Tests du contrat fadeIn/fadeOut exposé par PlaylistDataService."""

    def setUp(self):
        self.service = PlaylistDataService()

    def _playlist(self, playlist_type, fade_in=FadePlaylistEnum.DEFAULT.name, fade_out=FadePlaylistEnum.DEFAULT.name):
        return SimpleNamespace(
            uuid=uuid4(),
            typePlaylist=playlist_type,
            volume=75,
            useSpecificDelay=False,
            maxDelay=0,
            fadeIn=fade_in,
            fadeOut=fade_out,
        )

    def test_get_playlist_data_default_keeps_strategy_defaults(self):
        playlist = self._playlist(PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name)

        data = self.service.get_playlist_data(playlist)

        self.assertEqual(data['fadeInType'], FadeEnum.EASE.value)
        self.assertEqual(data['fadeInDuration'], 5)
        self.assertEqual(data['fadeOutType'], FadeEnum.EASE.value)
        self.assertEqual(data['fadeOutDuration'], 5)

    def test_get_playlist_data_off_disables_fade_and_sets_duration_zero(self):
        playlist = self._playlist(
            PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name,
            fade_in=FadeEnum.DISABLED.name,
            fade_out=FadeEnum.DISABLED.name,
        )

        data = self.service.get_playlist_data(playlist)

        self.assertEqual(data['fadeInType'], FadeEnum.DISABLED.value)
        self.assertEqual(data['fadeInDuration'], 3)
        self.assertEqual(data['fadeOutType'], FadeEnum.DISABLED.value)
        self.assertEqual(data['fadeOutDuration'], 3)

    def test_get_playlist_data_fade_enum_forces_curve_and_enables_fade(self):
        playlist = self._playlist(
            PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name,
            fade_in=FadeEnum.EASE_OUT.name,
            fade_out=FadeEnum.EASE_IN_OUT_QUAD.name,
        )

        data = self.service.get_playlist_data(playlist)

        self.assertEqual(data['fadeInType'], FadeEnum.EASE_OUT.value)
        self.assertEqual(data['fadeOutType'], FadeEnum.EASE_IN_OUT_QUAD.value)

    def test_get_playlist_data_unknown_fade_value_keeps_strategy_defaults(self):
        playlist = self._playlist(
            PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            fade_in='YES',
            fade_out='NO',
        )

        data = self.service.get_playlist_data(playlist)

        self.assertEqual(data['fadeInType'], FadeEnum.EASE.value)
        self.assertEqual(data['fadeOutType'], FadeEnum.EASE.value)
