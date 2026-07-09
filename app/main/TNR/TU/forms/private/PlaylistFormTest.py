from unittest.mock import patch

from django.test import RequestFactory, TestCase, tag

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.PlaylistTag import PlaylistTag
from main.architecture.persistence.models.User import User
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.service.PlaylistService import PlaylistService
from main.interface.ui.forms.private.PlaylistForm import PlaylistForm


@tag('unitaire')
class PlaylistFormTest(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = User.objects.create(username='testuser', email='test@test.com')
        self.tag = PlaylistTag.objects.create(name='Action', label='action', is_active=True)

    def test_save_persists_playlist_tags_on_update(self):
        playlist = Playlist.objects.create(
            user=self.user,
            name='Playlist test',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            color='#000000',
            colorText='#ffffff',
            volume=75,
        )

        form = PlaylistForm(
            data={
                'name': 'Playlist test',
                'typePlaylist': PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
                'useSpecificColor': 'on',
                'color': '#000000',
                'colorText': '#ffffff',
                'volume': 75,
                'is_copiable': 'on',
                'useSpecificDelay': '',
                'maxDelay': 0,
                'fadeIn': 'DEFAULT',
                'fadeOut': 'DEFAULT',
                'playlist_tags': [str(self.tag.pk)],
            },
            instance=playlist,
        )

        self.assertTrue(form.is_valid(), form.errors)
        updated_playlist = form.save()

        self.assertEqual(updated_playlist.playlist_tags.count(), 1)
        self.assertEqual(list(updated_playlist.playlist_tags.values_list('pk', flat=True)), [self.tag.pk])

    @patch('main.domain.common.service.PlaylistService.UserTierManager.get_user_limits')
    @patch('main.domain.common.service.PlaylistService.PlaylistRepository.count_private', return_value=0)
    def test_save_form_persists_playlist_tags_on_create(self, mock_count_private, mock_get_user_limits):
        mock_get_user_limits.return_value = {
            'soundboard': 10,
            'playlist': 10,
            'music_per_playlist': 50,
            'weight_music_mb': 100,
        }

        request = self.request_factory.post(
            '/playlist/create/',
            data={
                'name': 'Playlist test',
                'typePlaylist': PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
                'useSpecificColor': 'on',
                'color': '#000000',
                'colorText': '#ffffff',
                'volume': 75,
                'is_copiable': 'on',
                'useSpecificDelay': '',
                'maxDelay': 0,
                'fadeIn': 'DEFAULT',
                'fadeOut': 'DEFAULT',
                'playlist_tags': [str(self.tag.pk)],
            },
        )
        request.user = self.user

        playlist = PlaylistService(request).save_form()

        self.assertIsNotNone(playlist)
        self.assertEqual(playlist.playlist_tags.count(), 1)
        self.assertEqual(list(playlist.playlist_tags.values_list('pk', flat=True)), [self.tag.pk])