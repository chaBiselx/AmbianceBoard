import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, tag
from django.urls import reverse

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.SoundboardSection import SoundboardSection

User = get_user_model()


@tag('integration')
class OrganizeSoundboardUpdateRouteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='organize-user',
            email='organize-user@test.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='organize-other-user',
            email='organize-other-user@test.com',
            password='testpass123'
        )

        self.soundboard = SoundBoard.objects.create(
            user=self.user,
            name='Soundboard organize test'
        )
        self.other_soundboard = SoundBoard.objects.create(
            user=self.other_user,
            name='Other user soundboard organize test'
        )

        self.playlist_1 = Playlist.objects.create(name='Playlist 1', user=self.user)
        self.playlist_2 = Playlist.objects.create(name='Playlist 2', user=self.user)
        self.playlist_3 = Playlist.objects.create(name='Playlist 3', user=self.user)

        sections = [
            SoundboardSection.objects.create(
                SoundBoard=self.soundboard, section=section, name=f'Section {section}', order=section
            )
            for section in range(1, 4)
        ]

        self.sp_1 = SoundboardPlaylist.objects.create(
            SoundBoard=self.soundboard,
            Playlist=self.playlist_1,
            section=sections[0],
            order=1,
        )
        self.sp_2 = SoundboardPlaylist.objects.create(
            SoundBoard=self.soundboard,
            Playlist=self.playlist_2,
            section=sections[1],
            order=1,
        )
        self.sp_3 = SoundboardPlaylist.objects.create(
            SoundBoard=self.soundboard,
            Playlist=self.playlist_3,
            section=sections[2],
            order=1,
        )

    def test_organize_update_insert_section_shifts_sections(self):
        self.client.login(username='organize-user', password='testpass123')

        response = self.client.generic(
            method='UPDATE',
            path=reverse('organizeSoundboardUpdate', kwargs={'soundboard_uuid': self.soundboard.uuid}),
            data=json.dumps({'insertSection': 2}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)

        self.sp_1.refresh_from_db()
        self.sp_2.refresh_from_db()
        self.sp_3.refresh_from_db()

        self.assertEqual(self.sp_1.get_section(), 1)
        self.assertEqual(self.sp_2.get_section(), 3)
        self.assertEqual(self.sp_3.get_section(), 4)

    def test_organize_update_insert_section_denies_access_to_other_user_soundboard(self):
        self.client.login(username='organize-user', password='testpass123')

        response = self.client.generic(
            method='UPDATE',
            path=reverse('organizeSoundboardUpdate', kwargs={'soundboard_uuid': self.other_soundboard.uuid}),
            data=json.dumps({'insertSection': 1}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)
