from django.test import TestCase, RequestFactory, tag
from django.contrib.auth import get_user_model
from uuid import uuid4
from unittest.mock import patch, MagicMock

from main.domain.public.service.ReportContentService import ReportContentService
from main.architecture.persistence.models.ReportContent import ReportContent
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.domain.moderator.dto.TreatmentReportDto import TreatmentReportDto
from main.domain.moderator.service.TreatmentReportService import TreatmentReportService
from main.domain.public.decorator.detectBan import detect_ban
from main.domain.common.decorator.detectNotConfirmedAccount import detect_not_confirmed_account

User = get_user_model()

@tag('unitaire')
class ReportingModerationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='reporter', email='r@ex.com', password='pass', isConfirmed=True)  # NOSONAR
        self.moderator = User.objects.create_user(username='moderator', email='m@ex.com', password='pass', isConfirmed=True)  # NOSONAR
        self.target_user = User.objects.create_user(username='target', email='t@ex.com', password='pass', isConfirmed=True)  # NOSONAR
        self.soundboard = SoundBoard.objects.create(user=self.target_user, name='SB')

    @patch('main.domain.public.service.ReportContentService.ModeratorEmail')
    def test_report_content_success(self, mock_mail):
        request = self.factory.post('/report', data={
            'element-type': 'soundboard',
            'element-id': str(uuid4()),
            'element-precision': 'text',
            'element-description': 'Bad content'
        })
        request.user = self.user
        service = ReportContentService(request)
        report = service.save_report()
        self.assertIsNotNone(report)
        self.assertEqual(report.creator, self.user)

    def test_report_content_invalid_uuid(self):
        request = self.factory.post('/report', data={
            'element-type': 'soundboard',
            'element-id': 'INVALID_UUID',
        })
        request.user = self.user
        service = ReportContentService(request)
        report = service.save_report()
        self.assertIsNone(report)

    def test_treatment_report_service_update_and_log_and_ban(self):
        # Créer un report
        report = ReportContent.objects.create(
            typeElement='soundboard',
            uuidElement=uuid4(),
            precisionElement='text',
            descriptionElement='desc'
        )
        dto = TreatmentReportDto(
            content_report_accepted='on',
            content_report_id=report.id,
            content_moderator_response='CONTENT_REMOVED',
            moderator_log_accepted='on',
            moderator_log_message='Message',
            moderator_log_tag='TAG',
            moderator_log_model='UNKNOWN',
            action_ban_user='on',
            action_ban_duration='1',
            action_ban_reason='Abuse'
        )
        service = TreatmentReportService(dto, user=self.target_user, moderator=self.moderator)
        service.update_content_report()
        service.create_log_moderation()
        service.action_ban()
        report.refresh_from_db()
        self.target_user.refresh_from_db()
        self.assertIsNotNone(report.resultModerator)
        self.assertTrue(self.target_user.isBan)

    def test_decorateur_detect_ban(self):
        self.target_user.isBan = True
        from django.utils import timezone
        self.target_user.banExpiration = timezone.now() + timezone.timedelta(days=1)
        self.target_user.save()

        @detect_ban
        def view(request, soundboard_uuid):
            from django.http import HttpResponse
            return HttpResponse('OK')
        request = self.factory.get('/soundboard')
        request.user = self.target_user
        response = view(request, soundboard_uuid=str(self.soundboard.uuid))
        self.assertEqual(response.status_code, 404)

    def test_decorateur_detect_not_confirmed_account(self):
        self.user.isConfirmed = False
        self.user.save()

        @detect_not_confirmed_account()
        def view(request):
            from django.http import HttpResponse
            return HttpResponse('OK')
        request = self.factory.get('/test')
        request.user = self.user
        # Initialiser le système de messages pour éviter MessageFailure
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', {})
        messages_storage = FallbackStorage(request)
        setattr(request, '_messages', messages_storage)
        response = view(request)
        self.assertEqual(response.status_code, 200)
