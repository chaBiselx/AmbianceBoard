from datetime import timedelta
from unittest.mock import patch

from django.test import SimpleTestCase, tag
from django.utils import timezone

from main.domain.common.enum.ChartPeriodEnum import ChartPeriodEnum
from main.domain.common.helper.DurationHelper import DurationHelper
from main.domain.moderator.service.ModeratorSoundboardStatsService import ModeratorSoundboardStatsService


@tag('unitaire')
class ModeratorSoundboardStatsServiceTest(SimpleTestCase):
    def test_duration_format_preserves_seconds_and_hours_beyond_one_day(self):
        for seconds, expected in [(0, '00:00:00'), (59, '00:00:59'), (60, '00:01:00'),
                                  (3661, '01:01:01'), (90000, '25:00:00')]:
            with self.subTest(seconds=seconds):
                self.assertEqual(DurationHelper.format(timedelta(seconds=seconds)), expected)

    @patch('main.domain.moderator.service.ModeratorSoundboardStatsService.SoundBoardRepository')
    @patch('main.domain.moderator.service.ModeratorSoundboardStatsService.UserActivityRepository')
    def test_periods_use_rolling_date_range(self, activity_repository, soundboard_repository):
        now = timezone.now()
        activity_repository.return_value.get_soundboard_listening_summary.return_value = []
        soundboard_repository.return_value.get_list_by_ids.return_value = []
        with patch('main.domain.moderator.service.ModeratorSoundboardStatsService.timezone.now', return_value=now):
            period_choices = ChartPeriodEnum.get_days_mapping()
            for period in [*period_choices, '1', '30', '90', 'invalid', '']:
                with self.subTest(period=period):
                    expected_period = period if period in period_choices else '7'
                    result = ModeratorSoundboardStatsService().get_dashboard_listening_data(period)
                    self.assertEqual(result['listening_rows'], [])
                    self.assertEqual(result['listening_period'], expected_period)
                    self.assertEqual(result['listening_period_choices'], period_choices)
                    activity_repository.return_value.get_soundboard_listening_summary.assert_called_with(
                        now - timedelta(days=int(expected_period)), now,
                    )
        activity_repository.return_value.get_soundboard_listeners.assert_not_called()