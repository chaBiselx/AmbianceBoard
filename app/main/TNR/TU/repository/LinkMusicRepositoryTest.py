from django.test import TestCase, tag

from main.architecture.persistence.models.LinkMusic import LinkMusic
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.LinkMusicRepository import LinkMusicRepository
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum


@tag('unitaire')
class LinkMusicRepositoryTest(TestCase):
    def setUp(self):
        self.repository = LinkMusicRepository()
        user = User.objects.create_user(username='link-user', password='pw')
        playlist = Playlist.objects.create(
            user=user,
            name='Link playlist',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )
        self.link = LinkMusic.objects.create(
            playlist=playlist,
            url='https://example.com/audio.mp3',
            alternativeName='External audio',
        )

    def test_get_link_returns_existing_item(self):
        found = self.repository.get_link(self.link.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, self.link.id)

    def test_get_link_returns_none_when_missing(self):
        found = self.repository.get_link(999999)

        self.assertIsNone(found)
