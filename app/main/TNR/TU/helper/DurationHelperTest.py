from datetime import timedelta

from django.test import SimpleTestCase, tag

from main.domain.common.helper.DurationHelper import DurationHelper


@tag('unitaire')
class DurationHelperTest(SimpleTestCase):
    def test_format_returns_zero_padded_hours_minutes_and_seconds(self):
        cases = (
            (0, '00:00:00'),
            (59, '00:00:59'),
            (60, '00:01:00'),
            (3661, '01:01:01'),
            (90000, '25:00:00'),
        )

        for seconds, expected in cases:
            with self.subTest(seconds=seconds):
                self.assertEqual(
                    DurationHelper.format(timedelta(seconds=seconds)),
                    expected,
                )
