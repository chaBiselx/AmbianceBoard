from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from uuid import uuid4

from main.domain.public.service.ReportContentService import ReportContentService
from main.architecture.persistence.models.ReportContent import ReportContent
from main.domain.common.exceptions.PostDataException import PostDataException

User = get_user_model()

class ReportContentServiceTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', email='t@example.com', password='pass', isConfirmed=True)  # NOSONAR

    @patch('main.domain.public.service.ReportContentService.ModeratorEmail')
    def test_save_report_success_authenticated(self, mock_mail):
        request = self.factory.post('/report', data={
            'element-type': 'playlist',
            'element-id': str(uuid4()),
            'element-precision': 'image',
            'element-description': 'Inappropriate picture'
        })
        request.user = self.user
        service = ReportContentService(request)
        report = service.save_report()
        self.assertIsNotNone(report)
        self.assertEqual(report.creator, self.user)
        mock_mail.return_value.report_content_reported.assert_called_once()

    @patch('main.domain.public.service.ReportContentService.ModeratorEmail')
    def test_save_report_success_anonymous(self, mock_mail):
        request = self.factory.post('/report', data={
            'element-type': 'soundboard',
            'element-id': str(uuid4()),
            'element-precision': 'text',
        })
        # Anonymous user simulation
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        service = ReportContentService(request)
        report = service.save_report()
        self.assertIsNotNone(report)
        self.assertIsNone(report.creator)
        mock_mail.return_value.report_content_reported.assert_called_once()

    def test_save_report_non_post(self):
        request = self.factory.get('/report')
        request.user = self.user
        service = ReportContentService(request)
        self.assertIsNone(service.save_report())

    def test_save_report_invalid_uuid(self):
        request = self.factory.post('/report', data={
            'element-type': 'playlist',
            'element-id': 'NOT_A_UUID',
        })
        request.user = self.user
        service = ReportContentService(request)
        self.assertIsNone(service.save_report())
        self.assertEqual(ReportContent.objects.count(), 0)

    def test_save_report_invalid_type(self):
        request = self.factory.post('/report', data={
            'element-type': 'unknown_type',
            'element-id': str(uuid4()),
        })
        request.user = self.user
        service = ReportContentService(request)
        self.assertIsNone(service.save_report())
        self.assertEqual(ReportContent.objects.count(), 0)

    @patch('main.domain.public.service.ReportContentService.ModeratorEmail')
    def test_save_report_defaults(self, mock_mail):
        # precision defaults to 'unknown', description to ''
        request = self.factory.post('/report', data={
            'element-type': 'playlist',
            'element-id': str(uuid4()),
        })
        request.user = self.user
        service = ReportContentService(request)
        report = service.save_report()
        self.assertIsNotNone(report)
        self.assertEqual(report.precisionElement, 'unknown')
        self.assertEqual(report.descriptionElement, '')
        mock_mail.return_value.report_content_reported.assert_called_once()

    def test_save_report_missing_uuid(self):
        request = self.factory.post('/report', data={
            'element-type': 'playlist',
        })
        request.user = self.user
        service = ReportContentService(request)
        self.assertIsNone(service.save_report())
        self.assertEqual(ReportContent.objects.count(), 0)

    # ---------------- Helper methods tests ----------------
    def test__extract_post_data(self):
        u = str(uuid4())
        request = self.factory.post('/report', data={
            'element-type': 'playlist',
            'element-id': u,
            'element-precision': 'text',
            'element-description': 'Desc'
        })
        request.user = self.user
        service = ReportContentService(request)
        data = service._extract_post_data()
        self.assertEqual(data['type_element'], 'playlist')
        self.assertEqual(data['uuid_element'], u)
        self.assertEqual(data['precision_element'], 'text')
        self.assertEqual(data['description_element'], 'Desc')

    def test__validate_uuid_ok(self):
        request = self.factory.post('/report')
        request.user = self.user
        service = ReportContentService(request)
        try:
            service._validate_uuid(str(uuid4()))
        except PostDataException:
            self.fail("_validate_uuid raised PostDataException unexpectedly!")

    def test__validate_uuid_invalid(self):
        request = self.factory.post('/report')
        request.user = self.user
        service = ReportContentService(request)
        with self.assertRaises(PostDataException):
            service._validate_uuid('BAD_UUID')

    def test__is_valid_type_true(self):
        request = self.factory.post('/report')
        request.user = self.user
        service = ReportContentService(request)
        self.assertTrue(service._is_valid_type('playlist', str(uuid4())))

    def test__is_valid_type_false(self):
        request = self.factory.post('/report')
        request.user = self.user
        service = ReportContentService(request)
        self.assertFalse(service._is_valid_type('bad', str(uuid4())))

    def test__create_report_sets_creator(self):
        request = self.factory.post('/report')
        request.user = self.user
        service = ReportContentService(request)
        report = service._create_report('playlist', str(uuid4()), 'text', 'Desc')
        self.assertEqual(report.creator, self.user)

    def test__create_report_anonymous_no_creator(self):
        from django.contrib.auth.models import AnonymousUser
        request = self.factory.post('/report')
        request.user = AnonymousUser()
        service = ReportContentService(request)
        report = service._create_report('playlist', str(uuid4()), 'text', 'Desc')
        self.assertIsNone(report.creator)

    @patch('main.domain.public.service.ReportContentService.ModeratorEmail')
    def test__notify_moderators_success(self, mock_mail):
        request = self.factory.post('/report')
        request.user = self.user
        service = ReportContentService(request)
        report = service._create_report('playlist', str(uuid4()), 'text', 'Desc')
        service._notify_moderators(report)
        mock_mail.return_value.report_content_reported.assert_called_once_with(report)

    @patch('main.domain.public.service.ReportContentService.ModeratorEmail')
    def test__notify_moderators_logs_error(self, mock_mail):
        # Force exception in email sending
        mock_mail.return_value.report_content_reported.side_effect = Exception("SMTP failure")
        request = self.factory.post('/report')
        request.user = self.user
        service = ReportContentService(request)
        report = service._create_report('playlist', str(uuid4()), 'text', 'Desc')
        service._notify_moderators(report)  # Should not raise
