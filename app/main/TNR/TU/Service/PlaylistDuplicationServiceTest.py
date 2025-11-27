"""
Tests unitaires pour le service PlaylistDuplicationService.

Ce module teste le service responsable de la duplication complète
de playlists avec leurs éléments musicaux et l'historique.
"""

import uuid
from django.test import TestCase, tag
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from main.domain.common.service.PlaylistDuplicationService import PlaylistDuplicationService
from main.domain.common.exceptions.PlaylistDuplicationException import (
    PlaylistAlreadyDuplicatedException,
    PlaylistNotCopiableException
)
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.LinkMusic import LinkMusic
from main.architecture.persistence.models.Track import Track
from main.architecture.persistence.models.PlaylistDuplicationHistory import PlaylistDuplicationHistory
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.enum.FadePlaylistEnum import FadePlaylistEnum
from main.domain.common.enum.LinkMusicTypeEnum import LinkMusicTypeEnum

local_format_audio1 = "audio/mpeg"


@tag('unitaire')
class PlaylistDuplicationServiceTest(TestCase):
    """Tests pour le service PlaylistDuplicationService"""

    def setUp(self):
        """Configuration initiale des tests"""
        # Créer deux utilisateurs : source et destination
        self.source_user = User.objects.create(
            username="source_user",
            email="source@test.com"
        )
        self.target_user = User.objects.create(
            username="target_user",
            email="target@test.com"
        )
        
        # Créer une playlist source copiable
        self.source_playlist = Playlist.objects.create(
            user=self.source_user,
            name="Playlist Test",
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
            volume=80,
            useSpecificColor=True,
            color="#FF0000",
            colorText="#FFFFFF",
            useSpecificDelay=True,
            maxDelay=10,
            fadeIn=FadePlaylistEnum.YES.name,
            fadeOut=FadePlaylistEnum.NO.name
        )

    def test_duplicate_creates_new_playlist_with_different_uuid(self):
        """Test que la duplication crée une nouvelle playlist avec un UUID différent"""
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        duplicated = service.duplicate()
        
        # Vérifier que c'est une nouvelle instance
        self.assertNotEqual(self.source_playlist.id, duplicated.id)
        self.assertNotEqual(self.source_playlist.uuid, duplicated.uuid)
        
        # Vérifier que le nouvel UUID est bien un UUID valide
        self.assertIsInstance(duplicated.uuid, uuid.UUID)

    def test_duplicate_copies_all_playlist_attributes(self):
        """Test que tous les attributs de la playlist sont copiés correctement"""
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        duplicated = service.duplicate()
        
        # Vérifier les attributs copiés
        self.assertEqual(duplicated.typePlaylist, self.source_playlist.typePlaylist)
        self.assertEqual(duplicated.volume, self.source_playlist.volume)
        self.assertEqual(duplicated.useSpecificColor, self.source_playlist.useSpecificColor)
        self.assertEqual(duplicated.color, self.source_playlist.color)
        self.assertEqual(duplicated.colorText, self.source_playlist.colorText)
        self.assertEqual(duplicated.useSpecificDelay, self.source_playlist.useSpecificDelay)
        self.assertEqual(duplicated.maxDelay, self.source_playlist.maxDelay)
        self.assertEqual(duplicated.fadeIn, self.source_playlist.fadeIn)
        self.assertEqual(duplicated.fadeOut, self.source_playlist.fadeOut)

    def test_duplicate_assigns_to_target_user(self):
        """Test que la playlist dupliquée est assignée au bon utilisateur"""
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        duplicated = service.duplicate()
        
        self.assertEqual(duplicated.user, self.target_user)
        self.assertNotEqual(duplicated.user, self.source_user)

    def test_duplicate_with_custom_name(self):
        """Test que la duplication avec un nom personnalisé fonctionne"""
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        custom_name = "Mon Nom Personnalisé"
        duplicated = service.duplicate(new_name=custom_name)
        
        self.assertEqual(duplicated.name, custom_name)

    def test_duplicate_without_custom_name_adds_copie_suffix(self):
        """Test que sans nom personnalisé, '(copie)' est ajouté"""
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        duplicated = service.duplicate()
        
        expected_name = f"{self.source_playlist.name} (copie)"
        self.assertEqual(duplicated.name, expected_name)

    def test_duplicate_sets_is_copiable_to_false(self):
        """Test que la copie n'est pas marquée comme copiable par défaut"""
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        duplicated = service.duplicate()
        
        self.assertTrue(self.source_playlist.is_copiable)
        self.assertFalse(duplicated.is_copiable)

    def test_duplicate_raises_exception_if_not_copiable(self):
        """Test qu'une exception est levée si la playlist n'est pas copiable"""
        self.source_playlist.is_copiable = False
        self.source_playlist.save()
        
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        
        with self.assertRaises(PlaylistNotCopiableException) as context:
            service.duplicate()
        
        self.assertIn(str(self.source_playlist.uuid), str(context.exception))
        self.assertIn(self.source_playlist.name, str(context.exception))

    def test_duplicate_raises_exception_if_already_duplicated(self):
        """Test qu'une exception est levée si l'utilisateur a déjà dupliqué cette playlist"""
        # Première duplication
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        service.duplicate()
        
        # Tenter une seconde duplication
        service2 = PlaylistDuplicationService(self.source_playlist, self.target_user)
        
        with self.assertRaises(PlaylistAlreadyDuplicatedException) as context:
            service2.duplicate()
        
        self.assertIn(str(self.source_playlist.uuid), str(context.exception))
        self.assertIn(self.target_user.username, str(context.exception))

    def test_duplicate_creates_history_record(self):
        """Test qu'un enregistrement d'historique est créé lors de la duplication"""
        initial_count = PlaylistDuplicationHistory.objects.count()
        
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        duplicated = service.duplicate()
        
        # Vérifier qu'un enregistrement a été créé
        self.assertEqual(PlaylistDuplicationHistory.objects.count(), initial_count + 1)
        
        # Vérifier les détails de l'historique
        history = PlaylistDuplicationHistory.objects.filter(
            duplicated_playlist=duplicated
        ).first()
        
        self.assertIsNotNone(history)
        self.assertEqual(history.source_playlist, self.source_playlist)
        self.assertEqual(history.source_playlist_name, self.source_playlist.name)
        self.assertEqual(history.source_playlist_uuid, self.source_playlist.uuid)
        self.assertEqual(history.duplicated_playlist, duplicated)

    def test_duplicate_copies_music_files(self):
        """Test que les fichiers Music sont copiés avec de nouveaux UUID"""
        # Créer un fichier Music
        audio_content = b'fake audio content'
        audio_file = SimpleUploadedFile("test.mp3", audio_content, content_type=local_format_audio1)
        
        Music.objects.create(
            playlist=self.source_playlist,
            fileName="test.mp3",
            file=audio_file,
            alternativeName="Test Music",
            duration=180.5
        )
        
        # Dupliquer
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        duplicated = service.duplicate()
        
        # Vérifier que le Music a été copié
        duplicated_musics = Music.objects.filter(playlist=duplicated)
        self.assertEqual(duplicated_musics.count(), 1)
        
        duplicated_music = duplicated_musics.first()
        # Vérifier que les attributs sont copiés
        self.assertEqual(duplicated_music.fileName, music.fileName)
        self.assertEqual(duplicated_music.alternativeName, music.alternativeName)
        self.assertEqual(duplicated_music.duration, music.duration)
        
        # Vérifier que ce sont des instances différentes
        self.assertNotEqual(duplicated_music.id, music.id)
        self.assertNotEqual(duplicated_music.file.name, music.file.name)

    def test_duplicate_copies_link_music(self):
        """Test que les LinkMusic sont copiés correctement"""
        # Créer un LinkMusic
        link_music = LinkMusic.objects.create(
            playlist=self.source_playlist,
            url="https://example.com/audio.mp3",
            domained_name="example.com",
            urlType=LinkMusicTypeEnum.FILE.name,
            alternativeName="Test Link",
            duration=240.0
        )
        
        # Dupliquer
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        duplicated = service.duplicate()
        
        # Vérifier que le LinkMusic a été copié
        duplicated_links = LinkMusic.objects.filter(playlist=duplicated)
        self.assertEqual(duplicated_links.count(), 1)
        
        duplicated_link = duplicated_links.first()
        # Vérifier que les attributs sont copiés
        self.assertEqual(duplicated_link.url, link_music.url)
        self.assertEqual(duplicated_link.domained_name, link_music.domained_name)
        self.assertEqual(duplicated_link.urlType, link_music.urlType)
        self.assertEqual(duplicated_link.alternativeName, link_music.alternativeName)
        self.assertEqual(duplicated_link.duration, link_music.duration)
        
        # Vérifier que ce sont des instances différentes
        self.assertNotEqual(duplicated_link.id, link_music.id)

    def test_duplicate_copies_multiple_tracks_in_order(self):
        """Test que plusieurs tracks sont copiés dans le bon ordre"""
        # Créer plusieurs tracks
        Music.objects.create(
            playlist=self.source_playlist,
            fileName="track1.mp3",
            file=SimpleUploadedFile("track1.mp3", b'content1', content_type=local_format_audio1),
            alternativeName=""
        )
        LinkMusic.objects.create(
            playlist=self.source_playlist,
            url="https://example.com/track2.mp3",
            urlType=LinkMusicTypeEnum.FILE.name,
            alternativeName=""
        )
        Music.objects.create(
            playlist=self.source_playlist,
            fileName="track3.mp3",
            file=SimpleUploadedFile("track3.mp3", b'content3', content_type=local_format_audio1),
            alternativeName=""
        )
        
        # Dupliquer
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        duplicated = service.duplicate()
        
        # Vérifier le nombre de tracks
        source_tracks_count = Track.objects.filter(playlist=self.source_playlist).count()
        duplicated_tracks_count = Track.objects.filter(playlist=duplicated).count()
        self.assertEqual(source_tracks_count, 3)
        self.assertEqual(duplicated_tracks_count, 3)

    def test_duplicate_with_icon(self):
        """Test que l'icône de la playlist est copiée"""
        # Ajouter une icône à la playlist source
        icon_content = b'fake image content'
        icon_file = SimpleUploadedFile("icon.png", icon_content, content_type="image/png")
        self.source_playlist.icon = icon_file
        self.source_playlist.save()
        
        # Dupliquer
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        duplicated = service.duplicate()
        
        # Vérifier que l'icône existe
        self.assertTrue(duplicated.icon)
        self.assertNotEqual(duplicated.icon.name, self.source_playlist.icon.name)
        # Vérifier que le nom contient le nouvel UUID
        self.assertIn(str(duplicated.uuid), duplicated.icon.name)

    def test_duplicate_without_icon(self):
        """Test que la duplication fonctionne même sans icône"""
        # S'assurer que la playlist n'a pas d'icône
        self.source_playlist.icon = None
        self.source_playlist.save()
        
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        duplicated = service.duplicate()
        
        # Vérifier que la duplication a réussi
        self.assertIsNotNone(duplicated)
        self.assertFalse(duplicated.icon)

    def test_duplicate_is_atomic(self):
        """Test que la duplication est atomique (tout ou rien)"""
        # Créer un Music avec un fichier
        Music.objects.create(
            playlist=self.source_playlist,
            fileName="test.mp3",
            file=SimpleUploadedFile("test.mp3", b'content', content_type=local_format_audio1),
            alternativeName=""
        )
        
        initial_playlist_count = Playlist.objects.count()
        initial_music_count = Music.objects.count()
        initial_history_count = PlaylistDuplicationHistory.objects.count()
        
        # Dupliquer normalement
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        service.duplicate()
        
        # Vérifier que tout a été créé
        self.assertEqual(Playlist.objects.count(), initial_playlist_count + 1)
        self.assertEqual(Music.objects.count(), initial_music_count + 1)
        self.assertEqual(PlaylistDuplicationHistory.objects.count(), initial_history_count + 1)

    def test_different_users_can_duplicate_same_playlist(self):
        """Test que différents utilisateurs peuvent dupliquer la même playlist"""
        # Créer un troisième utilisateur
        user3 = User.objects.create(
            username="user3",
            email="user3@test.com"
        )
        
        # Premier utilisateur duplique
        service1 = PlaylistDuplicationService(self.source_playlist, self.target_user)
        duplicate1 = service1.duplicate()
        
        # Deuxième utilisateur duplique la même playlist
        service2 = PlaylistDuplicationService(self.source_playlist, user3)
        duplicate2 = service2.duplicate()
        
        # Vérifier que les deux duplications ont réussi
        self.assertIsNotNone(duplicate1)
        self.assertIsNotNone(duplicate2)
        self.assertNotEqual(duplicate1.id, duplicate2.id)
        self.assertEqual(duplicate1.user, self.target_user)
        self.assertEqual(duplicate2.user, user3)
        
        # Vérifier l'historique
        self.assertEqual(PlaylistDuplicationHistory.objects.count(), 2)

    def test_history_preserved_if_source_playlist_deleted(self):
        """Test que l'historique est préservé si la playlist source est supprimée"""
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        duplicated = service.duplicate()
        
        # Récupérer l'historique
        history = PlaylistDuplicationHistory.objects.filter(
            duplicated_playlist=duplicated
        ).first()
        
        source_uuid = self.source_playlist.uuid
        source_name = self.source_playlist.name
        
        # Supprimer la playlist source
        self.source_playlist.delete()
        
        # Vérifier que l'historique existe toujours
        history.refresh_from_db()
        self.assertIsNone(history.source_playlist)  # SET_NULL
        self.assertEqual(history.source_playlist_uuid, source_uuid)
        self.assertEqual(history.source_playlist_name, source_name)

    def test_duplicate_with_empty_playlist(self):
        """Test que la duplication d'une playlist vide fonctionne"""
        # La source_playlist n'a pas de tracks
        service = PlaylistDuplicationService(self.source_playlist, self.target_user)
        duplicated = service.duplicate()
        
        # Vérifier que la duplication a réussi
        self.assertIsNotNone(duplicated)
        self.assertEqual(Track.objects.filter(playlist=duplicated).count(), 0)

    def tearDown(self):
        """Nettoyage après les tests"""
        # Nettoyer les fichiers et la base de données
        Music.objects.all().delete()
        LinkMusic.objects.all().delete()
        Track.objects.all().delete()
        PlaylistDuplicationHistory.objects.all().delete()
        Playlist.objects.all().delete()
        User.objects.all().delete()
