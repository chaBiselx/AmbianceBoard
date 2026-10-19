from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

from django.test import TestCase, override_settings, tag
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import timedelta

from django.contrib.auth import get_user_model
from main.architecture.persistence.models.UserTier import UserTier
from main.architecture.persistence.models.UserTierHistory import UserTierHistory
from main.architecture.persistence.models.UserActivity import UserActivity
from main.architecture.persistence.models.DomainBlacklist import DomainBlacklist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SharedSoundboard import SharedSoundboard

from main.domain.cron.service.UserTierExpirationService import UserTierExpirationService
from main.domain.cron.service.PurgeOldStatsService import PurgeOldStatsService
from main.domain.cron.service.DomainBlacklistCronService import DomainBlacklistCronService
from main.domain.cron.service.SharedSoundboardService import SharedSoundboardService
from main.domain.cron.service.MediaFileStructureService import MediaFileStructureService

User = get_user_model()

@tag('unitaire')
class CronServicesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='premium', email='p@ex.com', password='pass', isConfirmed=True) # NOSONAR
        self.user2 = User.objects.create_user(username='standard', email='s@ex.com', password='pass', isConfirmed=True) # NOSONAR
        self.tier = UserTier.objects.create(user=self.user, tier_name='PREMIUM_BASIC', tier_expiry_date=timezone.now() - timedelta(days=1))
        self.tier2 = UserTier.objects.create(user=self.user2, tier_name='STANDARD')

    @patch('main.domain.cron.service.UserTierExpirationService.UserMail')
    def test_user_tier_expiration_service_downgrade(self, mock_mail):
        service = UserTierExpirationService()
        result = service.handle_expired_tiers()
        self.tier.refresh_from_db()
        self.assertEqual(result, 1)
        self.assertEqual(self.tier.tier_name, 'STANDARD')
        self.assertTrue(UserTierHistory.objects.filter(user=self.user).exists())

    def test_purge_user_activity_service(self):
        # Create old and recent activities
        old_activity = UserActivity.objects.create(user=self.user, activity_type='LOGIN')
        old_activity.start_date = timezone.now() - timedelta(days=400)
        old_activity.save(update_fields=['start_date'])
        recent_activity = UserActivity.objects.create(user=self.user, activity_type='LOGIN')
        service = PurgeOldStatsService()
        service.set_days_older(365)
        service.purge()
        self.assertFalse(UserActivity.objects.filter(id=old_activity.id).exists())
        self.assertTrue(UserActivity.objects.filter(id=recent_activity.id).exists())

    @patch('main.domain.cron.service.DomainBlacklistCronService.RemoteTextDomainProvider')
    def test_domain_blacklist_cron_service(self, mock_provider_cls):
        mock_provider = MagicMock()
        mock_provider.get_domains.return_value = {'disposable.com', 'temp.com', 'temp.com'} # NOSONAR
        mock_provider_cls.return_value = mock_provider
        service = DomainBlacklistCronService()
        service.domain_provider = [mock_provider]
        service.sync_blacklist()
        self.assertGreaterEqual(DomainBlacklist.objects.count(), 2)

    def test_shared_soundboard_service_purge(self):
        sb = SoundBoard.objects.create(user=self.user, name='SB1')
        shared = SharedSoundboard.objects.create(soundboard=sb)
        # Forcer expiration à la date actuelle pour être purgé
        shared.expiration_date = timezone.now() - timedelta(seconds=1)
        shared.save(update_fields=['expiration_date'])
        service = SharedSoundboardService()
        service.purge_expired_shared_soundboard()
        self.assertFalse(SharedSoundboard.objects.filter(id=shared.id).exists())


@tag('unitaire')
class MediaFileStructureServiceTest(TestCase):
    def test_normalize_music_files_moves_files_and_updates_database_paths(self):
        with TemporaryDirectory() as temp_dir:
            media_root = Path(temp_dir)
            nested_file = media_root / 'musics' / 'musics' / 'nested' / 'track.mp3'
            nested_file.parent.mkdir(parents=True)
            nested_file.write_bytes(b'audio')

            with override_settings(MEDIA_ROOT=media_root), patch(
                'main.domain.cron.service.MediaFileStructureService.Music.objects.filter'
            ) as filter_musics:
                moved, conflicts = MediaFileStructureService().normalize_music_files()

            destination = media_root / 'musics' / 'track.mp3'
            self.assertEqual((moved, conflicts), (1, 0))
            self.assertEqual(destination.read_bytes(), b'audio')
            self.assertFalse(nested_file.exists())
            filter_musics.assert_called_once_with(file='musics/musics/nested/track.mp3')
            filter_musics.return_value.update.assert_called_once_with(file='musics/track.mp3')

    @patch('main.domain.cron.service.MediaFileStructureService.uuid.uuid4')
    def test_normalize_music_files_renames_collision_with_uuid_and_updates_database_path(self, mock_uuid4):
        with TemporaryDirectory() as temp_dir:
            media_root = Path(temp_dir)
            nested_file = media_root / 'musics' / 'musics' / 'track.mp3'
            destination = media_root / 'musics' / 'track.mp3'
            uuid_destination = media_root / 'musics' / '123e4567-e89b-42d3-a456-426614174000.mp3'
            nested_file.parent.mkdir(parents=True)
            nested_file.write_bytes(b'nested')
            destination.write_bytes(b'existing')
            mock_uuid4.return_value = UUID('123e4567-e89b-42d3-a456-426614174000')

            with override_settings(MEDIA_ROOT=media_root), patch(
                'main.domain.cron.service.MediaFileStructureService.Music.objects.filter'
            ) as filter_musics:
                moved, conflicts = MediaFileStructureService().normalize_music_files()

            self.assertEqual((moved, conflicts), (1, 0))
            self.assertFalse(nested_file.exists())
            self.assertEqual(destination.read_bytes(), b'existing')
            self.assertEqual(uuid_destination.read_bytes(), b'nested')
            filter_musics.assert_called_once_with(file='musics/musics/track.mp3')
            filter_musics.return_value.update.assert_called_once_with(
                file='musics/123e4567-e89b-42d3-a456-426614174000.mp3'
            )

    @patch('main.domain.cron.service.MediaFileStructureService.uuid.uuid4')
    def test_normalize_music_files_retries_uuid_when_generated_destination_exists(self, mock_uuid4):
        with TemporaryDirectory() as temp_dir:
            media_root = Path(temp_dir)
            nested_file = media_root / 'musics' / 'musics' / 'track.mp3'
            nested_file.parent.mkdir(parents=True)
            nested_file.write_bytes(b'nested')
            (media_root / 'musics' / 'track.mp3').write_bytes(b'existing')
            existing_uuid_destination = (
                media_root / 'musics' / '123e4567-e89b-42d3-a456-426614174000.mp3'
            )
            existing_uuid_destination.write_bytes(b'already here')
            mock_uuid4.side_effect = [
                UUID('123e4567-e89b-42d3-a456-426614174000'),
                UUID('123e4567-e89b-42d3-a456-426614174001'),
            ]

            with override_settings(MEDIA_ROOT=media_root), patch(
                'main.domain.cron.service.MediaFileStructureService.Music.objects.filter'
            ) as filter_musics:
                moved, conflicts = MediaFileStructureService().normalize_music_files()

            new_destination = media_root / 'musics' / '123e4567-e89b-42d3-a456-426614174001.mp3'
            self.assertEqual((moved, conflicts), (1, 0))
            self.assertEqual(existing_uuid_destination.read_bytes(), b'already here')
            self.assertEqual(new_destination.read_bytes(), b'nested')
            filter_musics.return_value.update.assert_called_once_with(
                file='musics/123e4567-e89b-42d3-a456-426614174001.mp3'
            )
