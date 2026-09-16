from unittest.mock import Mock, patch

from django.test import SimpleTestCase, tag

from main.interface.ui.templatetags.SoundBoard import get_ordered_playlists

REPOSITORY_PATH = "main.architecture.persistence.repository.SoundboardPlaylistRepository.SoundboardPlaylistRepository"


@tag('unitaire')
class SoundBoardTemplateTagTest(SimpleTestCase):
    @patch(REPOSITORY_PATH)
    def test_get_ordered_playlists_owner_true_uses_private_mode(self, repository_class):
        soundboard = Mock()
        expected = [('section-1', ['playlist'])]
        repository = repository_class.return_value
        repository.get_sectioned_playlists.return_value = expected

        result = get_ordered_playlists(soundboard, True)

        self.assertEqual(result, expected)
        repository.get_sectioned_playlists.assert_called_once_with(soundboard, public=False)

    @patch(REPOSITORY_PATH)
    def test_get_ordered_playlists_owner_false_uses_public_mode(self, repository_class):
        soundboard = Mock()
        expected = [('section-1', ['playlist'])]
        repository = repository_class.return_value
        repository.get_sectioned_playlists.return_value = expected

        result = get_ordered_playlists(soundboard, False)

        self.assertEqual(result, expected)
        repository.get_sectioned_playlists.assert_called_once_with(soundboard, public=True)
