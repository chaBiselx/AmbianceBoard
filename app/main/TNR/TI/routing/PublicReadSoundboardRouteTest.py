"""
Test d'intégration pour la route: Lecture publique de soundboard (/public/soundboards/<uuid:soundboard_uuid>)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.Tag import Tag
from main.architecture.persistence.models.Playlist import Playlist
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class PublicReadSoundboardRouteTest(TestCase):
    """Tests pour la route de lecture publique de soundboard"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.test_uuid = uuid.uuid4()
        self.user = User.objects.create_user(username='public_read_owner', email='public_read_owner@test.com', password='Test1234!')
        self.playlist = Playlist.objects.create(
            user=self.user,
            name='Playlist Public Read SEO',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )

    def _create_public_soundboard(self, name='Donjon Nocturne', description_seo='Description SEO custom', tags=None):
        soundboard = SoundBoard.objects.create(
            user=self.user,
            name=name,
            descriptionSEO=description_seo,
            is_public=True,
        )
        soundboard.playlists.add(self.playlist)
        for tag in tags or []:
            soundboard.tags.add(tag)
        return soundboard
    
    def test_public_read_soundboard_accessible_without_auth(self):
        """Test que la route est accessible sans authentification"""
        soundboard = self._create_public_soundboard()
        response = self.client.get(
            reverse('publicReadSoundboard', kwargs={
                'soundboard_uuid': soundboard.uuid
            })
        )
        self.assertEqual(response.status_code, 200)
    
    def test_public_read_soundboard_with_invalid_uuid(self):
        """Test avec un UUID invalide"""
        response = self.client.get(
            reverse('publicReadSoundboard', kwargs={
                'soundboard_uuid': uuid.uuid4()
            })
        )
        self.assertIn(response.status_code, [404, 403])

    def test_public_read_soundboard_seo_dynamic(self):
        """La page de lecture publique rend les balises SEO dynamiques attendues."""
        tag_1 = Tag.objects.create(name='horror')
        tag_2 = Tag.objects.create(name='night')
        soundboard = self._create_public_soundboard(tags=[tag_1, tag_2])

        response = self.client.get(
            reverse('publicReadSoundboard', kwargs={'soundboard_uuid': soundboard.uuid})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<title>Donjon Nocturne | Soundboard public | AmbianceBoard</title>', html=False)
        self.assertContains(response, '<meta name="description" content="Description SEO custom"', html=False)
        self.assertContains(response, '<meta name="keywords" content="Donjon Nocturne, horror, night, soundboard public, ambiance jdr, playlist ambiance"', html=False)
        self.assertContains(response, '<meta property="og:title" content="Donjon Nocturne | Soundboard public | AmbianceBoard"', html=False)
        self.assertContains(response, f'<meta property="og:url" content="http://testserver/public/soundboards/{soundboard.uuid}"', html=False)
        self.assertContains(response, '<meta property="og:type" content="website"', html=False)
        self.assertContains(response, '<meta name="twitter:card" content="summary_large_image"', html=False)
        self.assertContains(response, '<meta name="twitter:title" content="Donjon Nocturne | Soundboard public | AmbianceBoard"', html=False)
        self.assertContains(response, f'<link rel="canonical" href="http://testserver/public/soundboards/{soundboard.uuid}"', html=False)
        self.assertContains(response, '<meta name="robots" content="index,follow"', html=False)
        self.assertContains(response, '"@type": "CreativeWork"', html=False)

    def test_public_read_soundboard_seo_description_fallback_from_name_and_tags(self):
        """Sans descriptionSEO, la description est construite avec le nom et les tags."""
        tag = Tag.objects.create(name='mystere')
        soundboard = self._create_public_soundboard(
            name='Temple Oublie',
            description_seo='',
            tags=[tag],
        )

        response = self.client.get(
            reverse('publicReadSoundboard', kwargs={'soundboard_uuid': soundboard.uuid})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta name="description" content="Temple Oublie - Soundboard public avec les tags: mystere."', html=False)

    def test_public_read_soundboard_json_ld_escapes_script_payload(self):
        """Le JSON-LD de lecture doit neutraliser une tentative de fermeture de script."""
        payload = '</script><script>window.__ab_read_xss__=1</script>'
        soundboard = self._create_public_soundboard(description_seo=payload)

        response = self.client.get(
            reverse('publicReadSoundboard', kwargs={'soundboard_uuid': soundboard.uuid})
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '</script><script>window.__ab_read_xss__=1</script>', html=False)
        self.assertContains(response, '\\u003c/script\\u003e\\u003cscript\\u003ewindow.__ab_read_xss__=1\\u003c/script\\u003e', html=False)
