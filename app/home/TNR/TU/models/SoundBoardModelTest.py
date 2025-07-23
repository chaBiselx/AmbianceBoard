from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from unittest.mock import patch, Mock
import uuid
from home.models.SoundBoard import SoundBoard
from home.models.User import User
from home.models.Playlist import Playlist
from home.models.SoundboardPlaylist import SoundboardPlaylist

class SoundBoardModelTest(TestCase):
    def setUp(self):
        """Initialisation des données de test"""
        self.user = User.objects.create(
            username="testuser",
            email="test@test.com"
        )
        
        self.playlist = Playlist.objects.create(
            name="Test Playlist",
            user=self.user
        )
        
        # Créer un faux fichier pour les tests
        self.test_icon = SimpleUploadedFile(
            name='test_icon.png',
            content=b'file_content',
            content_type='image/png'
        )

    def test_soundboard_creation(self):
        """Test la création basique d'un SoundBoard"""
        soundboard = SoundBoard.objects.create(
            user=self.user,
            name="Other Name"
        )
        SoundboardPlaylist.objects.create(
            SoundBoard=soundboard,
            Playlist=self.playlist,
            order=1  
        )
        
        self.assertTrue(isinstance(soundboard, SoundBoard))
        self.assertEqual(soundboard.name, "Other Name")
        self.assertEqual(soundboard.color, "#000000")  # Valeur par défaut
        self.assertEqual(soundboard.colorText, "#ffffff")  # Valeur par défaut
        self.assertFalse(soundboard.is_public)  # Valeur par défaut
        # Ne pas tester soundboard.icon directement car c'est un FieldFile

    def test_user_required(self):
        """Test que l'utilisateur est obligatoire"""
        with self.assertRaises(ValueError):
            SoundBoard.objects.create(
                name="required Name"
            )

    @patch('uuid.uuid4')
    @patch('home.message.ReduceSizeImgMessenger.reduce_size_img.apply_async')
    def test_icon_upload(self, mock_reduce_size, mock_uuid):
        """Test le téléchargement et le traitement de l'icône lors de la première utilsation"""
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_uuid.return_value = uuid.UUID(test_uuid)
        
        soundboard = SoundBoard.objects.create(
            user=self.user,
            name="Test upload SoundBoard",
            icon=self.test_icon
        )
        
        # Vérifier que le nom du fichier a été modifié
        self.assertTrue(soundboard.icon.name.endswith('.png'))
        
        # Vérifier que la tâche de redimensionnement a été appelée
        mock_reduce_size.assert_called_once_with(
            args=['SoundBoard', soundboard.id],
            queue='default',
            priority=1
        )

    @patch('uuid.uuid4')
    @patch('home.message.ReduceSizeImgMessenger.reduce_size_img.apply_async')
    def test_icon_new_upload(self, mock_reduce_size, mock_uuid):
        """Test le téléchargement et le traitement de l'icône lors de la second utilsation"""
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_uuid.return_value = uuid.UUID(test_uuid)
        
        soundboard = SoundBoard.objects.create(
            user=self.user,
            name="test New uplood"
        )
        
        # Ensuite, ajouter l'icône
        soundboard.icon = self.test_icon
        soundboard.clean()  # Cette ligne est importante pour marquer l'icône comme modifiée
        soundboard.save()
        
        # Vérifier que le nom du fichier a été modifié
        self.assertTrue(soundboard.icon.name.endswith('.png'))
        
        # Vérifier que la tâche de redimensionnement a été appelée
        mock_reduce_size.assert_called_once_with(
            args=['SoundBoard', soundboard.id],
            queue='default',
            priority=1
        )

    @patch('home.message.ReduceSizeImgMessenger.reduce_size_img.apply_async')
    def test_icon_update(self, mock_reduce_size):
        """Test la mise à jour de l'icône"""
        # Créer d'abord un SoundBoard sans icône
        soundboard = SoundBoard.objects.create(
            user=self.user,
            name="Icon Update SoundBoard"
        )
        
        # Mettre à jour avec une nouvelle icône
        soundboard.icon = SimpleUploadedFile(
            name='new_icon.png',
            content=b'new_content',
            content_type='image/png'
        )
        soundboard.clean()  # Important pour déclencher _icon_changed
        soundboard.save()
        
        # Vérifier que la tâche de redimensionnement a été appelée
        mock_reduce_size.assert_called_once_with(
            args=['SoundBoard', soundboard.id],
            queue='default',
            priority=1
        )

    def test_playlist_relationship(self):
        """Test les relations many-to-many avec les playlists"""
        soundboard = SoundBoard.objects.create(
            user=self.user,
            name="Playlist SoundBoard"
        )
        
        # Ajouter plusieurs playlists
        playlist2 = Playlist.objects.create(name="Test Playlist 2",user=self.user)
        SoundboardPlaylist.objects.create(
            SoundBoard=soundboard,
            Playlist=self.playlist,
            order=1  
        )
        SoundboardPlaylist.objects.create(
            SoundBoard=soundboard,
            Playlist=playlist2,
            order=2  
        )
        
        # Vérifier les relations
        self.assertEqual(soundboard.playlists.count(), 2)
        self.assertIn(self.playlist, soundboard.playlists.all())
        self.assertIn(playlist2, soundboard.playlists.all())

    def test_color_validation(self):
        """Test la validation des couleurs au format hexadécimal"""
        soundboard = SoundBoard.objects.create(
            user=self.user,
            name="Color SoundBoard",
            color="#FF0000",
            colorText="#00FF00"
        )
        
        self.assertEqual(soundboard.color, "#FF0000")
        self.assertEqual(soundboard.colorText, "#00FF00")

    def test_uuid_generation(self):
        """Test que l'UUID est généré automatiquement"""
        soundboard = SoundBoard.objects.create(
            user=self.user,
            name="UUID Generation SoundBoard"
        )
        
        self.assertIsNotNone(soundboard.uuid)
        self.assertTrue(isinstance(soundboard.uuid, uuid.UUID))

    def test_user_deletion_cascade(self):
        """Test que la suppression d'un utilisateur supprime ses soundboards"""
        soundboard = SoundBoard.objects.create(
            user=self.user,
            name="Test Delete ID"
        )
        
        self.user.delete()
        
        # Vérifier que le soundboard a été supprimé
        with self.assertRaises(SoundBoard.DoesNotExist):
            SoundBoard.objects.get(uuid=soundboard.uuid)

    def tearDown(self):
        """Nettoyage après les tests"""
        # Supprimer les fichiers créés pendant les tests
        for soundboard in SoundBoard.objects.all():
            if soundboard.icon:
                storage = soundboard.icon.storage
                if storage.exists(soundboard.icon.name):
                    storage.delete(soundboard.icon.name)