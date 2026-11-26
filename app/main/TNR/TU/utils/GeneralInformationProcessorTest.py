from datetime import timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

from django.contrib import messages
from django.contrib.messages.storage.cookie import CookieStorage
from django.http import HttpResponse
from django.template import Context, Engine
from django.test import RequestFactory, SimpleTestCase, tag
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import override

from main.architecture.contextProcessors import general_information_processor as processor
from main.architecture.persistence.models.GeneralNotification import GeneralNotification


@tag('unitaire')
class GeneralInformationProcessorTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.notifications = [
            GeneralNotification(
                uuid=uuid4(),
                message='<strong>Scheduled maintenance</strong>',
                class_name='warning',
                end_date=timezone.now() + timedelta(days=1),
            )
        ]
        for name, value in (
            ('__get_has_recent_async_download_jobs', False),
            ('__get_pending_playlist_proposals_count', 0),
        ):
            patcher = patch.object(processor, name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch.object(processor, 'GeneralNotificationService')
        self.service = patcher.start()
        self.addCleanup(patcher.stop)
        self.service.return_value.get_list_notifications.return_value = self.notifications

    def make_request(self, authenticated, cookie=''):
        request = self.factory.get('/', HTTP_COOKIE=cookie)
        request.user = Mock(is_authenticated=authenticated)
        request._messages = CookieStorage(request)
        return request

    def render_notifications(self, request):
        context = processor.general_information_processor(request)
        context.update({'messages': request._messages, 'request': request})
        template = Engine.get_default().get_template('Html/partial/structure/utils/message.html')
        return template.render(Context(context))

    def test_partial_renders_do_not_accumulate_notifications_or_consume_flash_messages(self):
        for authenticated in (False, True):
            with self.subTest(authenticated=authenticated):
                cookie = ''
                for index in range(3):
                    request = self.make_request(authenticated, cookie)
                    if index == 0:
                        messages.success(request, 'Saved successfully')
                    processor.general_information_processor(request)
                    response = HttpResponse('AJAX fragment without notifications')
                    request._messages.update(response)
                    if response.cookies:
                        cookie = response.cookies.output(header='', sep='; ')

                request = self.make_request(authenticated, cookie)
                html = self.render_notifications(request)

                self.assertEqual(html.count(self.notifications[0].message), 1)
                self.assertEqual(html.count('Saved successfully'), 1)
                self.assertIn('alert-warning', html)
                self.assertIn(f'data-meta-uuid="{self.notifications[0].uuid}"', html)
                dismiss_url = reverse('dismissGeneralNotification', args=[self.notifications[0].uuid])
                if authenticated:
                    self.assertIn(f'data-meta-url_dismiss="{dismiss_url}"', html)
                else:
                    self.assertNotIn('data-meta-url_dismiss', html)

                response = HttpResponse()
                request._messages.update(response)
                cookie = response.cookies.output(header='', sep='; ')
                next_html = self.render_notifications(self.make_request(authenticated, cookie))
                self.assertEqual(next_html.count(self.notifications[0].message), 1)
                self.assertNotIn('Saved successfully', next_html)

    def test_each_notification_keeps_its_own_metadata_and_style(self):
        second_notification = GeneralNotification(
            uuid=uuid4(),
            message='Service unavailable',
            class_name='error',
            end_date=timezone.now() + timedelta(days=1),
        )
        self.notifications.append(second_notification)

        html = self.render_notifications(self.make_request(True))

        for notification in self.notifications:
            self.assertEqual(html.count(f'data-meta-uuid="{notification.uuid}"'), 1)
            dismiss_url = reverse('dismissGeneralNotification', args=[notification.uuid])
            self.assertIn(f'data-meta-url_dismiss="{dismiss_url}"', html)
        self.assertIn('alert-danger', html)

    def test_notification_message_uses_request_language(self):
        self.notifications[0].message_en = '<strong>English maintenance</strong>'
        request = self.make_request(True)
        for language, expected, unexpected in (
            ('en', self.notifications[0].message_en, self.notifications[0].message),
            ('en-us', self.notifications[0].message_en, self.notifications[0].message),
            ('fr', self.notifications[0].message, self.notifications[0].message_en),
        ):
            with self.subTest(language=language):
                request.LANGUAGE_CODE = language
                html = self.render_notifications(request)
                self.assertIn(expected, html)
                self.assertNotIn(unexpected, html)
                self.assertIn(f'data-meta-uuid="{self.notifications[0].uuid}"', html)
                self.assertIn('alert-warning', html)

    def test_english_message_falls_back_to_french_when_empty(self):
        request = self.make_request(False)
        request.LANGUAGE_CODE = 'en'

        self.assertIn(self.notifications[0].message, self.render_notifications(request))

    def test_notification_uses_active_language_without_request_language(self):
        self.notifications[0].message_en = '<strong>English maintenance</strong>'
        with override('en'):
            html = self.render_notifications(self.make_request(False))

        self.assertIn(self.notifications[0].message_en, html)
