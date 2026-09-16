"""
Test d'intégration pour la route: soundboards read (/soundBoards/<uuid:soundboard_uuid>)
"""
from django.test import tag
from django.urls import reverse
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase
import uuid


@tag('integration')
class SoundboardsReadRouteTest(AuthenticatedTestCase):
    """Tests pour la route soundboards read"""
    
    def setUp(self):
        super().setUp()
        
        self.other_user = self.create_user(username='otheruser', password='testpass123')
        
        self.soundboard = self.create_soundboard(
            name='Test Soundboard',
            color='#FF0000',
            colorText='#FFFFFF',
        )
        
        self.playlist = self.create_playlist(
            name='Test Playlist',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )
        self.link_playlist(self.soundboard, self.playlist, order=1)
        
        self.other_soundboard = self.create_soundboard(
            user=self.other_user,
            name='Other User Soundboard',
        )
    
    def test_soundboardsread_requires_authentication(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(
            reverse('soundboardsRead', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_soundboardsread_accessible_when_authenticated(self):
        """Test que la route est accessible pour un utilisateur authentifié avec son propre soundboard"""
        self.login()
        response = self.client.get(
            reverse('soundboardsRead', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 200)
        # Vérifier que le template se rend correctement sans erreur
        self.assertContains(response, self.soundboard.name)
        # S'assurer que le contenu HTML est bien rendu (pas d'erreur de template)
        content = response.content.decode('utf-8')
        self.assertIn('soundboard-name', content)
        self.assertNotIn('TemplateSyntaxError', content)
    
    def test_soundboardsread_returns_404_for_nonexistent_soundboard(self):
        """Test que la route retourne 404 pour un soundboard inexistant"""
        self.login()
        non_existent_uuid = uuid.uuid4()
        response = self.client.get(
            reverse('soundboardsRead', kwargs={'soundboard_uuid': non_existent_uuid})
        )
        self.assertEqual(response.status_code, 404)
    
    def test_soundboardsread_denies_access_to_other_users_soundboard(self):
        """Test qu'un utilisateur ne peut pas accéder au soundboard d'un autre utilisateur"""
        self.login()
        response = self.client.get(
            reverse('soundboardsRead', kwargs={'soundboard_uuid': self.other_soundboard.uuid})
        )
        self.assertEqual(response.status_code, 404)
    
    def test_soundboardsread_contains_playlist_data(self):
        """Test que la page contient les données des playlists associées"""
        self.login()
        response = self.client.get(
            reverse('soundboardsRead', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('soundboard', response.context)
        self.assertEqual(response.context['soundboard'].uuid, self.soundboard.uuid)
    
    def test_soundboardsread_renders_correct_template(self):
        """Test que la route utilise le bon template"""
        self.login()
        response = self.client.get(
            reverse('soundboardsRead', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Html/Soundboard/soundboard_read.html')
    
    def test_soundboardsread_with_multiple_playlists(self):
        """Test l'affichage d'un soundboard avec plusieurs playlists"""
        # Créer plusieurs playlists
        playlist2 = self.create_playlist(
            name='Test Playlist 2',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )
        playlist3 = self.create_playlist(
            name='Test Playlist 3',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )
        self.link_playlist(self.soundboard, playlist2, order=2)
        self.link_playlist(self.soundboard, playlist3, order=3)
        
        self.login()
        response = self.client.get(
            reverse('soundboardsRead', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 200)
        # Vérifier que le soundboard a 3 playlists
        self.assertEqual(response.context['soundboard'].playlists.count(), 3)
    
    def test_soundboardsread_template_renders_without_syntax_error(self):
        """Test que le template se rend complètement sans erreur de syntaxe"""
        self.login()
        
        # Effectuer la requête - si une TemplateSyntaxError existe, elle sera levée ici
        response = self.client.get(
            reverse('soundboardsRead', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        
        # Vérifier que la réponse est 200
        self.assertEqual(response.status_code, 200)
        
        # Récupérer le contenu de la réponse
        content = response.content.decode('utf-8')
        
        # Vérifier que le contenu contient des éléments clés du template
        self.assertIn('soundboard-name', content)
        self.assertIn('playlist-element', content)
        
        # Vérifier qu'il n'y a pas de message d'erreur dans le contenu
        self.assertNotIn('TemplateSyntaxError', content)
        self.assertNotIn('Could not parse', content)
        
        # Vérifier que les données de la playlist sont présentes
        self.assertIn(str(self.playlist.uuid), content)
