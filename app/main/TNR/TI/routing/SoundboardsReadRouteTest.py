"""
Test d'intégration pour la route: soundboards read (/soundBoards/<uuid:soundboard_uuid>)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
import uuid

User = get_user_model()


@tag('integration')
class SoundboardsReadRouteTest(TestCase):
    """Tests pour la route soundboards read"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer un autre utilisateur pour tester les permissions
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Créer un soundboard pour l'utilisateur principal
        self.soundboard = SoundBoard.objects.create(
            user=self.user,
            name="Test Soundboard",
            color="#FF0000",
            colorText="#FFFFFF"
        )
        
        # Créer une playlist et l'associer au soundboard
        self.playlist = Playlist.objects.create(
            name="Test Playlist",
            user=self.user
        )
        
        SoundboardPlaylist.objects.create(
            SoundBoard=self.soundboard,
            Playlist=self.playlist,
            order=1
        )
        
        # Créer un soundboard pour l'autre utilisateur
        self.other_soundboard = SoundBoard.objects.create(
            user=self.other_user,
            name="Other User Soundboard"
        )
    
    def test_soundboardsread_requires_authentication(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(
            reverse('soundboardsRead', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_soundboardsread_accessible_when_authenticated(self):
        """Test que la route est accessible pour un utilisateur authentifié avec son propre soundboard"""
        self.client.login(username='testuser', password='testpass123')
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
        self.client.login(username='testuser', password='testpass123')
        non_existent_uuid = uuid.uuid4()
        response = self.client.get(
            reverse('soundboardsRead', kwargs={'soundboard_uuid': non_existent_uuid})
        )
        self.assertEqual(response.status_code, 404)
    
    def test_soundboardsread_denies_access_to_other_users_soundboard(self):
        """Test qu'un utilisateur ne peut pas accéder au soundboard d'un autre utilisateur"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('soundboardsRead', kwargs={'soundboard_uuid': self.other_soundboard.uuid})
        )
        self.assertEqual(response.status_code, 404)
    
    def test_soundboardsread_contains_playlist_data(self):
        """Test que la page contient les données des playlists associées"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('soundboardsRead', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('soundboard', response.context)
        self.assertEqual(response.context['soundboard'].uuid, self.soundboard.uuid)
    
    def test_soundboardsread_renders_correct_template(self):
        """Test que la route utilise le bon template"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('soundboardsRead', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Html/Soundboard/soundboard_read.html')
    
    def test_soundboardsread_with_multiple_playlists(self):
        """Test l'affichage d'un soundboard avec plusieurs playlists"""
        # Créer plusieurs playlists
        playlist2 = Playlist.objects.create(
            name="Test Playlist 2",
            user=self.user
        )
        playlist3 = Playlist.objects.create(
            name="Test Playlist 3",
            user=self.user
        )
        
        SoundboardPlaylist.objects.create(
            SoundBoard=self.soundboard,
            Playlist=playlist2,
            order=2
        )
        SoundboardPlaylist.objects.create(
            SoundBoard=self.soundboard,
            Playlist=playlist3,
            order=3
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('soundboardsRead', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 200)
        # Vérifier que le soundboard a 3 playlists
        self.assertEqual(response.context['soundboard'].playlists.count(), 3)
    
    def test_soundboardsread_template_renders_without_syntax_error(self):
        """Test que le template se rend complètement sans erreur de syntaxe"""
        self.client.login(username='testuser', password='testpass123')
        
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
