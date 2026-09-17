from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.SoundboardSection import SoundboardSection


User = get_user_model()


class TestDataMixin:
    def create_user(self, username='owner', email=None, password='pw', **overrides):
        return User.objects.create_user(
            username=username,
            email=email or f'{username}@test.com',
            password=password,
            **overrides,
        )

    def create_soundboard(self, user=None, name='Test soundboard', **overrides):
        return SoundBoard.objects.create(
            user=user or self.user,
            name=name,
            **overrides,
        )

    def create_playlist(self, user=None, name='Test playlist', **overrides):
        return Playlist.objects.create(
            user=user or self.user,
            name=name,
            **overrides,
        )

    def link_playlist(self, soundboard, playlist, section=1, order=1, **overrides):
        soundboard_section, _ = SoundboardSection.objects.get_or_create(
            SoundBoard=soundboard,
            section=section,
            defaults={'name': f'Section {section}', 'order': section},
        )
        return SoundboardPlaylist.objects.create(
            Playlist=playlist,
            section=soundboard_section,
            order=order,
            **overrides,
        )


class AuthenticatedTestCase(TestDataMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = self.create_user()

    def login(self, user=None, password='pw'):
        authenticated_user = user or self.user
        return self.client.login(username=authenticated_user.username, password=password)