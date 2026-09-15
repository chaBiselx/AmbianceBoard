"""
Test d'intégration pour la route: dismiss trace user activity (/trace-user-activity/<trace_user_activity_uuid>/dismiss/<type_activity>/)
"""
import uuid
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from main.architecture.persistence.repository.UserActivityRepository import UserActivityRepository
from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum

User = get_user_model()


@tag('integration')
class DismissTraceUserActivityRouteTest(TestCase):
    """Tests pour la route dismiss trace user activity"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )  # NOSONAR
        self.activity = UserActivityRepository().create(
            activity_type=UserActivityTypeEnum.LOGIN,
            user=self.user,
        )

    def test_dismiss_trace_user_activity_accessible_without_auth(self):
        """Test que la route est accessible sans authentification (pas de login_required)"""
        url = reverse('dismissTraceUserActivity', kwargs={
            'trace_user_activity_uuid': self.activity.uuid,
            'type_activity': UserActivityTypeEnum.LOGIN.value,
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), 'Trace user activity dismissed')

    def test_dismiss_trace_user_activity_sets_end_date(self):
        """Test que l'activité est bien terminée après l'appel"""
        url = reverse('dismissTraceUserActivity', kwargs={
            'trace_user_activity_uuid': self.activity.uuid,
            'type_activity': UserActivityTypeEnum.LOGIN.value,
        })
        self.client.post(url)
        self.activity.refresh_from_db()
        self.assertIsNotNone(self.activity.end_date)

    def test_dismiss_trace_user_activity_unknown_uuid_returns_error(self):
        """Test qu'une activité inconnue renvoie une erreur"""
        url = reverse('dismissTraceUserActivity', kwargs={
            'trace_user_activity_uuid': uuid.uuid4(),
            'type_activity': UserActivityTypeEnum.LOGIN.value,
        })
        response = self.client.post(url)
        self.assertIn(response.status_code, [404, 500])

    def test_dismiss_trace_user_activity_get_not_allowed(self):
        """Test que la méthode GET n'est pas acceptée"""
        url = reverse('dismissTraceUserActivity', kwargs={
            'trace_user_activity_uuid': self.activity.uuid,
            'type_activity': UserActivityTypeEnum.LOGIN.value,
        })
        response = self.client.get(url)
        self.assertIn(response.status_code, [400, 405, 406])
