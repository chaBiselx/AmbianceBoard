from django.test import TestCase, tag
from django.utils import timezone

from main.architecture.persistence.models.UserModerationLog import UserModerationLog
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.UserModerationLogRepository import UserModerationLogRepository


@tag('unitaire')
class UserModerationLogRepositoryTest(TestCase):
    def setUp(self):
        self.repository = UserModerationLogRepository()
        self.user = User.objects.create_user(username='moderated-user', password='pw')
        self.moderator = User.objects.create_user(username='moderator-user', password='pw')

    def test_create_persists_log(self):
        data = {
            'user': self.user,
            'moderator': self.moderator,
            'message': 'Please keep content respectful.',
            'tag': 'LANGUAGE',
            'model': 'USER',
        }

        created = self.repository.create(data)

        self.assertIsNotNone(created.id)
        self.assertEqual(created.user_id, self.user.id)
        self.assertEqual(created.moderator_id, self.moderator.id)

    def test_get_resume_moderation_returns_limited_ordered_queryset(self):
        old = UserModerationLog.objects.create(
            user=self.user,
            moderator=self.moderator,
            message='old',
            tag='SPAM',
            model='USER',
            created_at=timezone.now() - timezone.timedelta(days=1),
        )
        new = UserModerationLog.objects.create(
            user=self.user,
            moderator=self.moderator,
            message='new',
            tag='OTHER',
            model='USER',
            created_at=timezone.now(),
        )

        resume = list(self.repository.get_resume_moderation(self.user, limit=1))

        self.assertEqual(len(resume), 1)
        self.assertEqual(resume[0].id, old.id)
        self.assertNotEqual(resume[0].id, new.id)

    def test_get_all_queryset_returns_ordered_queryset(self):
        first = UserModerationLog.objects.create(
            user=self.user,
            moderator=self.moderator,
            message='1',
            tag='COPYRIGHT',
            model='USER',
            created_at=timezone.now() - timezone.timedelta(days=2),
        )
        second = UserModerationLog.objects.create(
            user=self.user,
            moderator=self.moderator,
            message='2',
            tag='HARASSMENT',
            model='USER',
            created_at=timezone.now() - timezone.timedelta(days=1),
        )

        result = list(self.repository.get_all_queryset())

        self.assertGreaterEqual(len(result), 2)
        self.assertEqual(result[0].id, first.id)
        self.assertEqual(result[1].id, second.id)
