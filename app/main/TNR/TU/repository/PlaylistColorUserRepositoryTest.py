from django.test import TestCase, tag

from main.architecture.persistence.models.PlaylistColorUser import PlaylistColorUser
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.PlaylistColorUserRepository import PlaylistColorUserRepository


@tag('unitaire')
class PlaylistColorUserRepositoryTest(TestCase):
    def setUp(self):
        self.repository = PlaylistColorUserRepository()
        self.user = User.objects.create_user(username='color-user', password='pw')
        self.other_user = User.objects.create_user(username='other-color-user', password='pw')

    def test_get_or_create_creates_then_reuses_same_record(self):
        first = self.repository.get_or_create(self.user, 'PLAYLIST_TYPE_MUSIC')
        second = self.repository.get_or_create(self.user, 'PLAYLIST_TYPE_MUSIC')

        self.assertEqual(first.id, second.id)
        self.assertEqual(
            PlaylistColorUser.objects.filter(user=self.user, typePlaylist='PLAYLIST_TYPE_MUSIC').count(),
            1,
        )

    def test_get_list_with_user_returns_only_user_rows(self):
        PlaylistColorUser.objects.create(user=self.user, typePlaylist='PLAYLIST_TYPE_MUSIC')
        PlaylistColorUser.objects.create(user=self.user, typePlaylist='PLAYLIST_TYPE_AMBIENT')
        PlaylistColorUser.objects.create(user=self.other_user, typePlaylist='PLAYLIST_TYPE_MUSIC')

        result = list(self.repository.get_list_with_user(self.user))

        self.assertEqual(len(result), 2)
        self.assertTrue(all(item.user_id == self.user.id for item in result))

    def test_get_list_with_user_and_type_filters_both_fields(self):
        match = PlaylistColorUser.objects.create(user=self.user, typePlaylist='PLAYLIST_TYPE_MUSIC')
        PlaylistColorUser.objects.create(user=self.user, typePlaylist='PLAYLIST_TYPE_AMBIENT')
        PlaylistColorUser.objects.create(user=self.other_user, typePlaylist='PLAYLIST_TYPE_MUSIC')

        result = list(self.repository.get_list_with_user_and_type(self.user, 'PLAYLIST_TYPE_MUSIC'))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, match.id)
