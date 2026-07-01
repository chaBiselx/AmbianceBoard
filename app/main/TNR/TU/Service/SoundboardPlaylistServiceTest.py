from django.test import TestCase, tag

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.User import User
from main.domain.common.service.SoundboardPlaylistService import SoundboardPlaylistService


@tag('unitaire')
class SoundboardPlaylistServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='soundboard-playlist-service-user',
            email='soundboard-playlist-service@test.com',
            password='testpass123'
        )
        self.soundboard = SoundBoard.objects.create(
            user=self.user,
            name='SB service test'
        )
        self.playlist_1 = Playlist.objects.create(name='Playlist 1', user=self.user)
        self.playlist_2 = Playlist.objects.create(name='Playlist 2', user=self.user)
        self.playlist_3 = Playlist.objects.create(name='Playlist 3', user=self.user)
        self.playlist_unassociated = Playlist.objects.create(name='Playlist unassociated', user=self.user)

        self.sp_1 = SoundboardPlaylist.objects.create(
            SoundBoard=self.soundboard,
            Playlist=self.playlist_1,
            section=1,
            order=1,
        )
        self.sp_2 = SoundboardPlaylist.objects.create(
            SoundBoard=self.soundboard,
            Playlist=self.playlist_2,
            section=2,
            order=1,
        )
        self.sp_3 = SoundboardPlaylist.objects.create(
            SoundBoard=self.soundboard,
            Playlist=self.playlist_3,
            section=3,
            order=1,
        )

    def test_insert_section_shifts_sections_from_index(self):
        service = SoundboardPlaylistService(self.soundboard)

        service.insert_section(2)

        self.sp_1.refresh_from_db()
        self.sp_2.refresh_from_db()
        self.sp_3.refresh_from_db()

        self.assertEqual(self.sp_1.section, 1)
        self.assertEqual(self.sp_2.section, 3)
        self.assertEqual(self.sp_3.section, 4)

    def test_update_does_not_create_soundboard_playlist_when_playlist_is_unassociated(self):
        service = SoundboardPlaylistService(self.soundboard)

        service.update(self.playlist_unassociated, order=1, section=2)

        self.assertFalse(
            SoundboardPlaylist.objects.filter(
                SoundBoard=self.soundboard,
                Playlist=self.playlist_unassociated,
            ).exists()
        )

    def test_add_does_not_duplicate_existing_soundboard_playlist(self):
        service = SoundboardPlaylistService(self.soundboard)
        initial_count = SoundboardPlaylist.objects.filter(
            SoundBoard=self.soundboard,
            Playlist=self.playlist_1,
        ).count()

        service.add(self.playlist_1, order=1, section=1)

        self.assertEqual(
            SoundboardPlaylist.objects.filter(
                SoundBoard=self.soundboard,
                Playlist=self.playlist_1,
            ).count(),
            initial_count,
        )
