from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from unittest.mock import patch
import uuid
from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User

filename_name1 = "Test Music"
filename_alt1 = "Alt Name"


class MusicModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')  # NOSONAR
        """Initialisation des données de test"""
        self.playlist = Playlist.objects.create(
            name="Test Playlist",
            user=self.user
        )
        
        # Créer un faux fichier pour les tests
        self.test_file = SimpleUploadedFile(
            name='test_music.mp3',
            content=b'file_content',
            content_type='audio/mp3'
        )

    def test_music_creation(self):
        """Test la création basique d'un objet Music"""
        music = Music.objects.create(
            fileName=filename_name1,
            alternativeName=filename_alt1,
            file=self.test_file,
            playlist=self.playlist
        )
        
        self.assertTrue(isinstance(music, Music))
        self.assertEqual(music.alternativeName, filename_alt1)
        self.assertTrue(music.file.name.endswith('.mp3'))
        self.assertEqual(music.playlist, self.playlist)

    @patch('uuid.uuid4')
    def test_file_rename_on_save(self, mock_uuid):
        """Test que le nom du fichier est bien modifié avec UUID lors de la sauvegarde"""
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_uuid.return_value = uuid.UUID(test_uuid)
        
        music = Music.objects.create(
            fileName="Original Name",
            alternativeName=filename_alt1,
            file=SimpleUploadedFile(
                name='test_long_name_that_needs_truncating.mp3',
                content=b'file_content'
            ),
            playlist=self.playlist
        )
        
        # Vérifier que le nom du fichier a bien été modifié avec l'UUID
        self.assertTrue(music.file.name.startswith(f"musics/{test_uuid}"))
        self.assertTrue(music.file.name.endswith('.mp3'))

    def test_filename_truncation(self):
        """Test que le fileName est bien tronqué à 63 caractères"""
        long_name = "a" * 100 + ".mp3"
        
        music = Music.objects.create(
            file=SimpleUploadedFile(name=long_name, content=b'content'),
            alternativeName=filename_alt1,
            playlist=self.playlist
        )
        
        self.assertEqual(len(music.fileName), 63)

    def test_playlist_deletion_cascade(self):
        """Test que la suppression d'une playlist supprime aussi les musiques associées"""
        music = Music.objects.create(
            fileName=filename_name1,
            alternativeName=filename_alt1,
            file=self.test_file,
            playlist=self.playlist
        )
        
        _ = self.playlist.uuid
        self.playlist.delete()
        
        # Vérifier que la musique a été supprimée
        with self.assertRaises(Music.DoesNotExist):
            Music.objects.get(id=music.id)

    def test_required_fields(self):
        """Test que les champs requis sont bien obligatoires"""
        # Test sans fichier
        music = Music(
            fileName=filename_name1,
            playlist=self.playlist
        )
        with self.assertRaises(ValidationError):
            music.full_clean()

    def test_music_str_method(self):
        """Test la méthode __str__ du modèle"""
        music = Music.objects.create(
            fileName=filename_name1,
            alternativeName=filename_alt1,
            file=self.test_file,
            playlist=self.playlist
        )
        

        self.assertEqual(music.alternativeName, str(music))

    def tearDown(self):
        """Nettoyage après les tests"""
        # Supprimer les fichiers créés pendant les tests
        for music in Music.objects.all():
            if music.file:
                storage = music.file.storage
                if storage.exists(music.file.name):
                    storage.delete(music.file.name)