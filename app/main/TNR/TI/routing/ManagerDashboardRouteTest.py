"""
Test d'intégration pour la route: manager dashboard (/manager/)
"""
from urllib.parse import urlencode
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.html import escape
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.architecture.persistence.models.TrafficAttributionVisit import TrafficAttributionVisit

User = get_user_model()


@tag('integration')
class ManagerDashboardRouteTest(TestCase):
    """Tests pour la route manager dashboard"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        role_group, _ = Group.objects.get_or_create(name='ROLE_ADMIN')
        self.user.groups.add(role_group)

    def grant_manager_permission(self):
        permission, _ = Permission.objects.get_or_create(
            codename=PermissionEnum.MANAGER_EXECUTE_BATCHS.name,
            content_type=ContentType.objects.get_for_model(Group),
            defaults={'name': 'Manager execute batchs'},
        )
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

    def test_dashboard_provides_existing_sources_and_absolute_home_url(self):
        self.grant_manager_permission()
        for source in ['newsletter', 'google', 'newsletter', '', '  ']:
            TrafficAttributionVisit.objects.create(utm_source=source, path='/public/soundboards')

        for period in ['0', '7']:
            response = self.client.get(reverse('managerDashboard'), {'periode-chart': period})
            self.assertEqual(200, response.status_code)
            self.assertEqual(['google', 'newsletter'], response.context['existing_utm_sources'])
            self.assertEqual('http://testserver/', response.context['home_share_base_url'])
            self.assertContains(response, '<option value="google">google</option>', html=True)
            self.assertContains(response, '<option value="newsletter">newsletter</option>', html=True)
            self.assertContains(response, 'id="home-share-copy"')

    def test_dashboard_without_sources(self):
        self.grant_manager_permission()
        response = self.client.get(reverse('managerDashboard'))

        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.context['existing_utm_sources'])
        self.assertContains(response, 'Aucune source UTM disponible')
        self.assertContains(response, '<select id="home-share-source" class="form-select" '
                            'data-home-url="http://testserver/" disabled>'
                            '<option value="">Aucune source UTM disponible</option></select>', html=True)

    def test_dashboard_escapes_source_values(self):
        self.grant_manager_permission()
        source = 'newsletter & "été" <test>'
        TrafficAttributionVisit.objects.create(utm_source=source)
        response = self.client.get(reverse('managerDashboard'))

        self.assertEqual(200, response.status_code)
        escaped_source = escape(source)
        self.assertContains(response, f'<option value="{escaped_source}">{escaped_source}</option>')

    def test_shared_home_link_tracks_exact_source_in_a_fresh_session(self):
        self.grant_manager_permission()
        response = self.client.get(reverse('managerDashboard'))
        self.assertEqual(200, response.status_code)
        source = ' été & + # ? '
        share_url = response.context['home_share_base_url'] + '?' + urlencode({'utm_source': source})

        home_response = Client().get(share_url, HTTP_ACCEPT='text/html')

        self.assertEqual(200, home_response.status_code)
        visit = TrafficAttributionVisit.objects.get(path=reverse('home'))
        self.assertEqual(source, visit.utm_source)
        self.assertEqual({'utm_source': source}, visit.utm_data)
        self.assertFalse(visit.is_authenticated)

    def test_dashboard_share_tool_requires_authentication(self):
        response = self.client.get(reverse('managerDashboard'))
        self.assertEqual(302, response.status_code)
        self.assertNotIn('home_share_base_url', response.content.decode())
    
    def test_managerdashboard_accessible_when_authenticated(self):
        """Test que la route manager dashboard est accessible pour un utilisateur avec le rôle ROLE_ADMIN"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerDashboard'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_managerdashboard_requires_role(self):
        """Test que la route nécessite le rôle ROLE_ADMIN"""
        # Utilisateur sans le rôle
        _ = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='normalpass123'
        )
        self.client.login(username='normaluser', password='normalpass123')
        response = self.client.get(reverse('managerDashboard'))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_manager_user_activity_details_accessible_when_authenticated(self):
        """Test que la route de détail d'activité utilisateur est accessible pour un admin"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerUserActivityDetails', kwargs={'user_uuid': self.user.uuid}))
        self.assertIn(response.status_code, [200, 302])

    def test_manager_referer_activity_dashboard_accessible_when_authenticated(self):
        """Test que la route JSON de stats referer est accessible pour un admin"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerRefererActivityDashboard'))
        self.assertIn(response.status_code, [200, 302])

    def test_manager_utm_source_activity_dashboard_accessible_when_authenticated(self):
        """Test que la route JSON de stats utm_source est accessible pour un admin"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('managerUtmSourceActivityDashboard'))
        self.assertIn(response.status_code, [200, 302])

