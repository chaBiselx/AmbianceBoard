"""
Test d'integration pour la route: moderator soundboard listing (/moderator/soundboard)
"""
from datetime import timedelta

from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from main.architecture.persistence.models.SoundBoard import SoundBoard

User = get_user_model()


@tag('integration')
class ModeratorListingSoundboardRouteTest(TestCase):
    """Tests pour la route moderator soundboard listing"""

    def setUp(self):
        self.client = Client()
        self.moderator = User.objects.create_superuser(
            username='moderator-soundboard',
            email='moderator-soundboard@example.com',
            password='testpass123'
        )
        self.owner_1 = User.objects.create_user(
            username='owner-one',
            email='owner-one@example.com',
            password='testpass123'
        )
        self.owner_2 = User.objects.create_user(
            username='owner-two',
            email='owner-two@example.com',
            password='testpass123'
        )

    def _create_soundboard(self, name: str, user: User, days_ago: int) -> SoundBoard:
        soundboard = SoundBoard.objects.create(name=name, user=user)
        if days_ago > 0:
            SoundBoard.objects.filter(pk=soundboard.pk).update(
                created_at=timezone.now() - timedelta(days=days_ago)
            )
            soundboard.refresh_from_db()
        return soundboard

    def test_listing_accessible_for_superuser(self):
        self.client.force_login(self.moderator)
        response = self.client.get(reverse('moderatorControleImagesSoundboard'))
        self.assertEqual(response.status_code, 200)

    def test_filter_by_username(self):
        self.client.force_login(self.moderator)
        kept = self._create_soundboard('SB owner1', self.owner_1, days_ago=5)
        self._create_soundboard('SB owner2', self.owner_2, days_ago=5)

        response = self.client.get(
            reverse('moderatorControleImagesSoundboard'),
            {'user': str(self.owner_1.uuid)}
        )

        self.assertEqual(response.status_code, 200)
        page_objects = list(response.context['page_objects'])
        self.assertEqual([kept.pk], [item.pk for item in page_objects])

    def test_filter_by_creation_period(self):
        self.client.force_login(self.moderator)
        kept = self._create_soundboard('SB recent', self.owner_1, days_ago=10)
        self._create_soundboard('SB old', self.owner_1, days_ago=200)

        response = self.client.get(
            reverse('moderatorControleImagesSoundboard'),
            {'period': '31'}
        )

        self.assertEqual(response.status_code, 200)
        page_objects = list(response.context['page_objects'])
        self.assertEqual([kept.pk], [item.pk for item in page_objects])

    def test_filter_user_and_period_combined(self):
        self.client.force_login(self.moderator)
        kept = self._create_soundboard('SB owner1 recent', self.owner_1, days_ago=10)
        self._create_soundboard('SB owner1 old', self.owner_1, days_ago=120)
        self._create_soundboard('SB owner2 recent', self.owner_2, days_ago=10)

        response = self.client.get(
            reverse('moderatorControleImagesSoundboard'),
            {
                'user': str(self.owner_1.uuid),
                'period': '31',
            }
        )

        self.assertEqual(response.status_code, 200)
        page_objects = list(response.context['page_objects'])
        self.assertEqual([kept.pk], [item.pk for item in page_objects])

    def test_filter_by_invalid_user_value_does_not_break_listing(self):
        self.client.force_login(self.moderator)
        self._create_soundboard('SB owner1', self.owner_1, days_ago=5)

        response = self.client.get(
            reverse('moderatorControleImagesSoundboard'),
            {'user': 'owner-one'}
        )

        self.assertEqual(response.status_code, 200)
