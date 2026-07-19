from django.test import TestCase, tag

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.PlaylistTag import PlaylistTag
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.PlaylistTagRepository import PlaylistTagRepository
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum


@tag("unitaire")
class PlaylistTagRepositoryTest(TestCase):
    def setUp(self):
        self.repository = PlaylistTagRepository()
        self.user = User.objects.create_user(username="playlist-tag-user", password="pw")  # NOSONAR

        self.tag_combat = PlaylistTag.objects.create(name="combat", is_active=True)
        self.tag_city = PlaylistTag.objects.create(name="city", is_active=True)
        self.tag_inactive = PlaylistTag.objects.create(name="hidden", is_active=False)

        self.playlist = Playlist.objects.create(
            user=self.user,
            name="Playlist 1",
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )
        self.playlist.playlist_tags.add(self.tag_combat)

    def test_get_list_active_tags_excludes_inactive(self):
        result = self.repository.get_list_active_tags()
        names = [tag.name for tag in result]

        self.assertIn("combat", names)
        self.assertIn("city", names)
        self.assertNotIn("hidden", names)

    def test_get_tag_with_count_returns_only_used_active_tags(self):
        result = self.repository.get_tag_with_count()
        names = [tag.name for tag in result]

        self.assertIn("combat", names)
        self.assertNotIn("city", names)
        self.assertNotIn("hidden", names)
