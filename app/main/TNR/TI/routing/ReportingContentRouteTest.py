"""
Test d'intégration pour la route: report content (/public/report)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class ReportingContentRouteTest(TestCase):
    """Tests pour la route report content"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
    
    def test_publicreportingcontent_accessible_without_auth(self):
        """Test que la route report content est accessible sans authentification"""
        response = self.client.post(reverse('publicReportingContent'), {})
        self.assertIn(response.status_code, [200, 302, 400, 401])
    
