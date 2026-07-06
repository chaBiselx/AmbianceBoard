from unittest.mock import Mock

from django.test import SimpleTestCase, tag

from main.interface.ui.templatetags.SoundBoard import get_ordered_playlists


@tag('unitaire')
class SoundBoardTemplateTagTest(SimpleTestCase):
    def test_get_ordered_playlists_owner_true_uses_private_mode(self):
        soundboard = Mock()
        expected = [('section-1', ['playlist'])]
        soundboard.get_list_playlist_ordered.return_value = expected

        result = get_ordered_playlists(soundboard, True)

        self.assertEqual(result, expected)
        soundboard.get_list_playlist_ordered.assert_called_once_with(public=False)

    def test_get_ordered_playlists_owner_false_uses_public_mode(self):
        soundboard = Mock()
        expected = [('section-1', ['playlist'])]
        soundboard.get_list_playlist_ordered.return_value = expected

        result = get_ordered_playlists(soundboard, False)

        self.assertEqual(result, expected)
        soundboard.get_list_playlist_ordered.assert_called_once_with(public=True)
