"""
Test d'intégration pour la route: public soundboards listing (/public/soundboards)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.Tag import Tag
from main.architecture.persistence.models.Playlist import Playlist
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class PublicListingSoundboardRouteTest(TestCase):
    """Tests pour la route public soundboards listing"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(username='public_listing_owner', email='public_listing_owner@test.com', password='Test1234!')
        self.playlist = Playlist.objects.create(
            user=self.user,
            name='Playlist Public SEO',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )

    def _create_public_soundboard(self, name='SB SEO', tags=None):
        soundboard = SoundBoard.objects.create(user=self.user, name=name, is_public=True)
        soundboard.playlists.add(self.playlist)
        for tag in tags or []:
            soundboard.tags.add(tag)
        return soundboard
    
    def test_publiclistingsoundboard_accessible_without_auth(self):
        """Test que la route public soundboards listing est accessible sans authentification"""
        self._create_public_soundboard()
        response = self.client.get(reverse('publicListingSoundboard'))
        self.assertEqual(response.status_code, 200)

    def test_public_listing_soundboard_seo_with_tag(self):
        """Le listing public rend des balises SEO dynamiques pour un tag sélectionné."""
        selected_tag = Tag.objects.create(name='dragon')
        other_tag = Tag.objects.create(name='epic')
        self._create_public_soundboard(tags=[selected_tag, other_tag])

        response = self.client.get(reverse('publicListingSoundboard'), {'tag': selected_tag.name})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta name="description" content="Decouvrez des soundboards publics pour le tag dragon sur AmbianceBoard."', html=False)
        self.assertContains(response, '<meta name="keywords" content="dragon, epic, soundboard, soundboard public, ambiance jdr, jeux de role, playlist ambiance, ambiance musicale"', html=False)
        self.assertContains(response, '<meta property="og:title" content="Soundboards publics - Tag dragon | AmbianceBoard"', html=False)
        self.assertContains(response, '<meta property="og:url" content="http://testserver/public/soundboards?tag=dragon"', html=False)
        self.assertContains(response, '<meta name="twitter:title" content="Soundboards publics - Tag dragon | AmbianceBoard"', html=False)
        self.assertContains(response, '<link rel="canonical" href="http://testserver/public/soundboards?tag=dragon"', html=False)
        self.assertContains(response, '<meta name="robots" content="index,follow"', html=False)
        self.assertContains(response, '"@type": "CollectionPage"', html=False)

    def test_public_listing_soundboard_seo_noindex_when_empty(self):
        """Le listing vide doit etre noindex,follow avec un JSON-LD de type WebPage."""
        response = self.client.get(reverse('publicListingSoundboard'), {'tag': 'inconnu'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta name="robots" content="noindex,follow"', html=False)
        self.assertContains(response, '<link rel="canonical" href="http://testserver/public/soundboards?tag=inconnu"', html=False)
        self.assertContains(response, '"@type": "WebPage"', html=False)

    def test_public_listing_soundboard_seo_noindex_when_page_gt_1(self):
        """Le listing page > 1 doit passer en noindex,follow."""
        for index in range(101):
            self._create_public_soundboard(name=f'SB SEO {index}')

        response = self.client.get(reverse('publicListingSoundboard'), {'page': 2})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta name="robots" content="noindex,follow"', html=False)

    def test_public_listing_soundboard_json_ld_escapes_script_payload(self):
        """Le JSON-LD du listing doit neutraliser une tentative de fermeture de script."""
        payload = '</script><script>window.__ab_listing_xss__=1</script>'

        response = self.client.get(reverse('publicListingSoundboard'), {'tag': payload})

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '</script><script>window.__ab_listing_xss__=1</script>', html=False)
        self.assertContains(response, '\\u003c/script\\u003e\\u003cscript\\u003ewindow.__ab_listing_xss__=1\\u003c/script\\u003e', html=False)
    
