from django.test import TestCase, tag

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.SoundboardSection import SoundboardSection
from main.architecture.persistence.models.Track import Track
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum


@tag('unitaire')
class SoundboardPlaylistRepositoryTest(TestCase):
    def setUp(self):
        self.repository = SoundboardPlaylistRepository()
        self.user = User.objects.create_user(username='sp-repo-user', password='pw')  # NOSONAR
        self.soundboard = SoundBoard.objects.create(user=self.user, name='Board')

        self.playlist_with_tracks = Playlist.objects.create(
            user=self.user,
            name='Playlist with tracks',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )
        self.playlist_without_tracks = Playlist.objects.create(
            user=self.user,
            name='Playlist without tracks',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )

        section_1 = SoundboardSection.objects.create(
            SoundBoard=self.soundboard, section=1, name='Section 1', order=1
        )
        section_2 = SoundboardSection.objects.create(
            SoundBoard=self.soundboard, section=2, name='Section 2', order=2
        )

        SoundboardPlaylist.objects.create(
            SoundBoard=self.soundboard,
            Playlist=self.playlist_with_tracks,
            section=section_1,
            order=1,
        )
        SoundboardPlaylist.objects.create(
            SoundBoard=self.soundboard,
            Playlist=self.playlist_without_tracks,
            section=section_2,
            order=1,
        )

        Track.objects.create(playlist=self.playlist_with_tracks, alternativeName='track-1')
        Track.objects.create(playlist=self.playlist_with_tracks, alternativeName='track-2')

    def test_get_all_with_min_one_track_returns_each_playlist_once(self):
        result = self.repository.get_all_with_min_one_track(self.soundboard)

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().Playlist.id, self.playlist_with_tracks.id)

    def test_get_playlist_formated_public_excludes_playlists_without_track(self):
        result = dict(self.repository.get_playlist_formated(self.soundboard, public=True))

        self.assertEqual(result[1], [self.playlist_with_tracks])
        self.assertEqual(result[2], [])

    def test_can_create_empty_section_with_name(self):
        section = SoundboardSection.objects.create(
            SoundBoard=self.soundboard,
            section=3,
            name='Section vide',
            order=3,
        )

        self.assertEqual(section.name, 'Section vide')
        self.assertEqual(section.SoundBoard, self.soundboard)
        self.assertEqual(section.section, 3)
        self.assertFalse(
            SoundboardPlaylist.objects.filter(
                SoundBoard=self.soundboard,
                section__section=3,
            ).exists()
        )
