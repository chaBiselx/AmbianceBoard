from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, tag

from main.architecture.messaging.email.TrackLabelReportEmail import TrackLabelReportEmail


@tag('unitaire')
class TrackLabelReportEmailTest(TestCase):
    @patch('main.architecture.messaging.email.TrackLabelReportEmail.Settings.get', return_value='support@example.com')
    @patch('main.architecture.messaging.email.TrackLabelReportEmail.EmailSender')
    def test_sends_track_labels_and_reporter_details_to_configured_contact(self, mock_sender, _mock_settings):
        track = SimpleNamespace(
            id=17,
            get_name=lambda: 'Forest rain',
            playlist=SimpleNamespace(name='Forest', uuid='playlist-uuid'),
        )
        labels = [SimpleNamespace(category='environment', label='rain', confidence=0.82)]
        reporter = SimpleNamespace(username='reporter', uuid='user-uuid', email='reporter@example.com')
        mock_sender.return_value.send_email.return_value = True

        result = TrackLabelReportEmail().send_report(track, labels, reporter)

        self.assertTrue(result)
        mock_sender.return_value.send_email.assert_called_once()
        kwargs = mock_sender.return_value.send_email.call_args.kwargs
        self.assertEqual(kwargs['from_email'], 'support@example.com')
        self.assertEqual(kwargs['to_emails'], ['support@example.com'])
        self.assertEqual(kwargs['reply_to_email'], 'reporter@example.com')
        self.assertFalse(kwargs['is_html'])
        self.assertIn('Forest rain (ID: 17)', kwargs['body'])
        self.assertIn('Username: reporter', kwargs['body'])
        self.assertIn('UUID: user-uuid', kwargs['body'])
        self.assertIn('environment: rain (82%)', kwargs['body'])

    @patch('main.architecture.messaging.email.TrackLabelReportEmail.Settings.get', return_value=None)
    @patch('main.architecture.messaging.email.TrackLabelReportEmail.EmailSender')
    def test_requires_configured_contact_email(self, mock_sender, _mock_settings):
        with self.assertRaises(ValueError):
            TrackLabelReportEmail().send_report(None, [], None)

        mock_sender.assert_not_called()