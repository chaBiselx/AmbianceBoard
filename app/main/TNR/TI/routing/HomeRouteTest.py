"""
Test d'intégration pour la route: home (/)
"""
import re

from django.test import TestCase, Client, tag
from django.urls import reverse

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.Track import Track
from main.architecture.persistence.models.User import User
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum


@tag('integration')
class HomeRouteTest(TestCase):
    """Tests pour la route home"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
    
    def test_home_accessible_without_auth(self):
        """Test que la page home est accessible sans authentification"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_home_returns_html(self):
        """Test que la route home retourne du HTML"""
        response = self.client.get(reverse('home'))
        self.assertIn('text/html', response.get('Content-Type', ''))

    def test_home_includes_content_security_policy_header(self):
        response = self.client.get(reverse('home'))

        self.assertIn('Content-Security-Policy', response)
        self.assertIn("default-src 'self'", response['Content-Security-Policy'])
        self.assertIn("form-action 'self'", response['Content-Security-Policy'])
        self.assertIn("style-src-attr 'unsafe-inline'", response['Content-Security-Policy'])
        self.assertNotIn(' ws: ', response['Content-Security-Policy'])
        self.assertNotIn(' wss: ', response['Content-Security-Policy'])

    def test_not_found_response_includes_content_security_policy_header(self):
        response = self.client.get('/missing-csp-test-route/')

        self.assertEqual(response.status_code, 404)
        self.assertIn('Content-Security-Policy', response)

    def test_google_tag_manager_script_uses_the_csp_nonce(self):
        with self.settings(APP_ENV='prod'):
            response = self.client.get(reverse('home'))

        nonce_match = re.search(r'<script nonce="([^"]+)"', response.content.decode())
        self.assertIsNotNone(nonce_match)
        self.assertIn(
            f"'nonce-{nonce_match.group(1)}'",
            response['Content-Security-Policy'],
        )

    def test_home_renders_french_copy(self):
        response = self.client.get(reverse('home'), HTTP_ACCEPT_LANGUAGE='fr-FR,fr;q=0.9')

        self.assertContains(response, 'Donnez vie à vos parties.')
        self.assertContains(response, 'Essayez une ambiance')

    def test_home_renders_english_copy(self):
        response = self.client.get(reverse('home'), HTTP_ACCEPT_LANGUAGE='en-US,en;q=0.9')

        self.assertContains(response, 'Bring your adventures to life.')
        self.assertContains(response, 'Try a soundscape')

    def test_home_exposes_community_copyable_playlist_and_track_counts(self):
        owner = User.objects.create_user(username='community-owner', password='pw')
        playlist = Playlist.objects.create(
            user=owner,
            name='Community playlist',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
        )
        Track.objects.create(playlist=playlist, alternativeName='Community track')

        response = self.client.get(reverse('home'))

        self.assertEqual(response.context['home_community_stats'], {'playlists': 1, 'tracks': 1})
