from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from main.domain.common.repository.TrackRepository import TrackRepository
from main.models.Music import Music
from main.models.LinkMusic import LinkMusic
from main.models.Playlist import Playlist
from main.models.User import User
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum


class TrackRepositoryTest(TestCase):
	def setUp(self):
		# Patch celery task to avoid launching async processing
		patcher = patch('main.message.ReduceBiteRateMessenger.reduce_bit_rate.apply_async')
		self.mock_apply_async = patcher.start()
		self.addCleanup(patcher.stop)

		self.user1 = User.objects.create_user(username='user1', password='pw')
		self.user2 = User.objects.create_user(username='user2', password='pw')

		self.playlist_user1 = Playlist.objects.create(
			user=self.user1,
			name='Playlist User1',
			typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
		)
		self.playlist_user2 = Playlist.objects.create(
			user=self.user2,
			name='Playlist User2',
			typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
		)

		# Create sample uploaded files
		self.file1 = SimpleUploadedFile('song1.mp3', b'aaa', content_type='audio/mp3')
		self.file2 = SimpleUploadedFile('song2.mp3', b'bbb', content_type='audio/mp3')
		self.music1 = Music.objects.create(fileName='song1', alternativeName='Song 1', file=self.file1, playlist=self.playlist_user1)
		self.music2 = Music.objects.create(fileName='song2', alternativeName='Song 2', file=self.file2, playlist=self.playlist_user1)
		self.link1 = LinkMusic.objects.create(url='https://example.com/audio.mp3', alternativeName='Link 1', playlist=self.playlist_user1)
		self.music_other_user = Music.objects.create(
			fileName='other',
			alternativeName='Other',
			file=SimpleUploadedFile('other.mp3', b'ccc', content_type='audio/mp3'),
			playlist=self.playlist_user2
		)

		self.repo = TrackRepository()

	def test_get_existing_track(self):
		track = self.repo.get(music_id=self.music1.id, playlist_uuid=self.playlist_user1.uuid)
		self.assertIsNotNone(track)
		self.assertEqual(track.id, self.music1.id)

	def test_get_non_existing_track_id(self):
		track = self.repo.get(music_id=999999, playlist_uuid=self.playlist_user1.uuid)
		self.assertIsNone(track)

	def test_get_track_wrong_playlist(self):
		track = self.repo.get(music_id=self.music1.id, playlist_uuid=self.playlist_user2.uuid)
		self.assertIsNone(track)

	def test_get_count(self):
		count = self.repo.get_count(self.playlist_user1)
		self.assertEqual(count, 3)  # 2 music + 1 link

	def test_get_random_public_returns_track(self):
		found = self.repo.get_random_public(self.playlist_user1.uuid)
		self.assertIsNotNone(found)
		self.assertIn(found.id, [self.music1.id, self.music2.id, self.link1.id])

	def test_get_random_public_empty(self):
		empty_playlist = Playlist.objects.create(
			user=self.user1,
			name='Empty',
			typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
		)
		found = self.repo.get_random_public(empty_playlist.uuid)
		self.assertIsNone(found)

	def test_get_random_private_with_owner_user(self):
		found = self.repo.get_random_private(self.playlist_user1.uuid, self.user1)
		self.assertIsNotNone(found)
		self.assertIn(found.id, [self.music1.id, self.music2.id, self.link1.id])

	def test_get_random_private_with_other_user_returns_none(self):
		found = self.repo.get_random_private(self.playlist_user1.uuid, self.user2)
		self.assertIsNone(found)

	def test_get_random_private_empty_playlist(self):
		empty_playlist = Playlist.objects.create(
			user=self.user1,
			name='Empty2',
			typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
		)
		found = self.repo.get_random_private(empty_playlist.uuid, self.user1)
		self.assertIsNone(found)
   
