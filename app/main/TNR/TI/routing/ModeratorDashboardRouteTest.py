"""
Test d'intégration pour la route: moderator dashboard (/moderator/)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.UserActivity import UserActivity
from main.architecture.persistence.repository.UserActivityRepository import UserActivityRepository
from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum
from main.domain.moderator.service.ModeratorSoundboardStatsService import ModeratorSoundboardStatsService

User = get_user_model()


@tag('integration')
class ModeratorDashboardRouteTest(TestCase):
    """Tests pour la route moderator dashboard"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        role_group, _ = Group.objects.get_or_create(name='ROLE_MODERATOR')
        self.user.groups.add(role_group)
    
    def test_moderatordashboard_accessible_when_authenticated(self):
        """Test que la route moderator dashboard est accessible pour un utilisateur avec le rôle ROLE_MODERATOR"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('moderatorDashboard'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_moderatordashboard_requires_role(self):
        """Test que la route nécessite le rôle ROLE_MODERATOR"""
        # Utilisateur sans le rôle
        _ = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='normalpass123'
        )
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('moderatorDashboard'))
        self.assertIn(response.status_code, [302, 403, 404])


@tag('integration')
class ModeratorListeningSummaryTest(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.start = self.now - timedelta(days=7)
        self.user = User.objects.create_user(username='listener')
        self.soundboard = SoundBoard.objects.create(user=self.user, name='Recent board')
        self.other = SoundBoard.objects.create(user=self.user, name='Other board')
        self.content_type = ContentType.objects.get_for_model(SoundBoard)

    def create_session(self, soundboard, minutes, user=None, started=None, **kwargs):
        start = started or self.now - timedelta(hours=2)
        return UserActivity.objects.create(
            content_type=self.content_type,
            object_id=soundboard.pk,
            activity_type=UserActivityTypeEnum.SOUNDBOARD_VIEW.value,
            start_date=start,
            end_date=start + timedelta(minutes=minutes) if minutes is not None else None,
            user=user,
            **kwargs,
        )

    def test_summary_orders_totals_and_averages_sessions(self):
        self.create_session(self.soundboard, 10, self.user)
        self.create_session(self.soundboard, 20, self.user)
        self.create_session(self.soundboard, 30)
        self.create_session(self.other, 40)
        repository = UserActivityRepository()
        rows = list(repository.get_soundboard_listening_summary(self.start, self.now))
        self.assertEqual([row['object_id'] for row in rows], [self.soundboard.pk, self.other.pk])
        self.assertEqual(rows[0]['total_duration'], timedelta(minutes=60))
        self.assertEqual(rows[0]['average_duration'], timedelta(minutes=20))
        listeners = list(repository.get_soundboard_listeners(self.start, self.now))
        self.assertEqual(len(listeners), 3)
        self.assertIn({'object_id': self.soundboard.pk, 'user__username': 'listener'}, listeners)
        self.assertIn({'object_id': self.soundboard.pk, 'user__username': None}, listeners)

    def test_summary_excludes_old_future_unfinished_invalid_and_unrelated_sessions(self):
        self.create_session(self.soundboard, 10, started=self.start - timedelta(seconds=1))
        self.create_session(self.soundboard, 10, started=self.now + timedelta(minutes=1))
        self.create_session(self.soundboard, None)
        self.create_session(self.soundboard, -10)
        unrelated = self.create_session(self.soundboard, 10)
        unrelated.activity_type = UserActivityTypeEnum.LOGIN.value
        unrelated.save(update_fields=['activity_type'])
        self.assertEqual(list(UserActivityRepository().get_soundboard_listening_summary(self.start, self.now)), [])

    def test_service_formats_ranking_and_listeners(self):
        self.create_session(self.soundboard, 10, self.user)
        self.create_session(self.soundboard, 20, self.user)
        self.create_session(self.soundboard, 30)
        self.create_session(self.other, 40)
        data = ModeratorSoundboardStatsService().get_dashboard_listening_data()
        self.assertEqual(data['listening_period'], '7')
        rows = data['listening_rows']
        self.assertEqual([row['position'] for row in rows], [1, 2])
        self.assertEqual(rows[0]['soundboard'], self.soundboard)
        self.assertEqual(rows[0]['total_duration'], '01:00:00')
        self.assertEqual(rows[0]['average_duration'], '00:20:00')
        self.assertEqual(rows[0]['listeners'], ['listener'])
        self.assertTrue(rows[0]['has_anonymous_listeners'])

    def test_service_filters_period_and_defaults_invalid_values(self):
        self.create_session(self.soundboard, 10, started=self.now - timedelta(days=10))
        service = ModeratorSoundboardStatsService()
        self.assertEqual(service.get_dashboard_listening_data('7')['listening_rows'], [])
        for period in ['14', '31', '61', '91', '183', '365', '1', '30', '90', 'invalid', '']:
            with self.subTest(period=period):
                data = service.get_dashboard_listening_data(period)
                valid_period = period in ['14', '31', '61', '91', '183', '365']
                self.assertEqual(len(data['listening_rows']), 1 if valid_period else 0)
                self.assertEqual(data['listening_period'], period if valid_period else '7')

    def test_service_ignores_deleted_soundboards(self):
        self.create_session(self.soundboard, 10)
        self.soundboard.delete()
        self.assertEqual(ModeratorSoundboardStatsService().get_dashboard_listening_data()['listening_rows'], [])

    def test_dashboard_renders_listening_table_for_moderator(self):
        role, _ = Group.objects.get_or_create(name='ROLE_MODERATOR')
        permission, _ = Permission.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(Group),
            codename='MODERATEUR_ACCESS_DASHBOARD',
            defaults={'name': 'Moderator dashboard access'},
        )
        role.permissions.add(permission)
        self.user.groups.add(role)
        self.client.force_login(self.user)
        self.create_session(self.soundboard, 15, self.user)
        self.create_session(self.soundboard, 15)
        SoundBoard.objects.filter(pk=self.soundboard.pk).update(icon='soundBoardIcon/test-icon.png')
        response = self.client.get(reverse('moderatorDashboard'), {'period': '31'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['listening_period'], '31')
        self.assertContains(response, 'Recent board')
        self.assertContains(response, '00:30:00')
        self.assertContains(response, '00:15:00')
        self.assertContains(response, 'listener')
        self.assertContains(response, 'soundBoardIcon/test-icon.png')
        self.assertTrue(response.context['listening_rows'][0]['has_anonymous_listeners'])
        self.assertContains(response, '<option value="31" selected>', html=False)
        response = self.client.get(reverse('moderatorDashboard'), {'period': 'invalid'})
        self.assertEqual(response.context['listening_period'], '7')
        response = self.client.get(reverse('moderatorDashboard'), {'period': '14'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Recent board')

    def test_dashboard_does_not_expose_listening_data_without_permission(self):
        self.client.force_login(self.user)
        self.create_session(self.soundboard, 15, self.user)
        response = self.client.get(reverse('moderatorDashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(b'Recent board', response.content)

