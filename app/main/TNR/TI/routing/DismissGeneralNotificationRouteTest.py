"""
Test d'intégration pour la route: dismiss general notification (/notification/dismiss/<notification_uuid>/)
"""
import uuid
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from main.architecture.persistence.models.GeneralNotification import GeneralNotification

User = get_user_model()


@tag('integration')
class DismissGeneralNotificationRouteTest(TestCase):
    """Tests pour la route dismiss general notification"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )  # NOSONAR
        self.notification = GeneralNotification.objects.create(
            message='Hello world',
            end_date=timezone.now() + timezone.timedelta(days=1),
        )

    def test_dismiss_general_notification_accessible_when_authenticated(self):
        """Test qu'un utilisateur authentifié peut rejeter une notification"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('dismissGeneralNotification', kwargs={'notification_uuid': self.notification.uuid})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), 'Notification dismissed')

    def test_dismiss_general_notification_requires_auth(self):
        """Test que la route nécessite une authentification"""
        url = reverse('dismissGeneralNotification', kwargs={'notification_uuid': self.notification.uuid})
        response = self.client.post(url)
        self.assertIn(response.status_code, [302, 401, 403])

    def test_dismiss_general_notification_unknown_uuid_returns_error(self):
        """Test qu'une notification inconnue renvoie une erreur"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('dismissGeneralNotification', kwargs={'notification_uuid': uuid.uuid4()})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 500)

    def test_dismiss_general_notification_get_not_allowed(self):
        """Test que la méthode GET n'est pas acceptée"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('dismissGeneralNotification', kwargs={'notification_uuid': self.notification.uuid})
        response = self.client.get(url)
        self.assertIn(response.status_code, [400, 405, 406])
