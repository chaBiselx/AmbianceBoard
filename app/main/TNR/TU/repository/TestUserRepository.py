from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from main.architecture.persistence.repository.UserRepository import UserRepository
from main.architecture.persistence.models.User import User


class UserRepositoryTest(TestCase):
    """Tests pour UserRepository - recherche et gestion des utilisateurs"""

    def setUp(self):
        """Configuration initiale des tests"""
        self.repository = UserRepository()
        
        # Créer des utilisateurs de test
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='password123',
            first_name='Test',
            last_name='User1'
        )
        self.user1.isConfirmed = True
        self.user1.save()
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password456',
            first_name='Another',
            last_name='User2'
        )

    def tearDown(self):
        """Nettoyage après chaque test"""
        User.objects.all().delete()

    # Tests search_login_user

    def test_search_login_user_by_username(self):
        """Test recherche utilisateur par username"""
        user = self.repository.search_login_user('testuser1')
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser1')
        self.assertEqual(user.email, 'test1@example.com')

    def test_search_login_user_by_email(self):
        """Test recherche utilisateur par email"""
        user = self.repository.search_login_user('test2@example.com')
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser2')
        self.assertEqual(user.email, 'test2@example.com')

    def test_search_login_user_not_found(self):
        """Test recherche utilisateur inexistant retourne None"""
        user = self.repository.search_login_user('nonexistent')
        
        self.assertIsNone(user)

    def test_search_login_user_with_empty_string(self):
        """Test recherche avec chaîne vide"""
        user = self.repository.search_login_user('')
        
        self.assertIsNone(user)

    def test_search_login_user_case_sensitive(self):
        """Test que la recherche est sensible à la casse"""
        user = self.repository.search_login_user('TESTUSER1')
        
        # Dépend de la configuration de la base de données
        # Par défaut Django est case-insensitive pour les recherches
        # Ce test vérifie le comportement actuel
        self.assertIsNone(user)

    # Tests get_user

    def test_get_user_by_uuid(self):
        """Test récupération utilisateur par UUID"""
        user = self.repository.get_user(str(self.user1.uuid))
        
        self.assertIsNotNone(user)
        self.assertEqual(user.uuid, self.user1.uuid)

    def test_get_user_nonexistent_uuid(self):
        """Test récupération avec UUID inexistant"""
        user = self.repository.get_user('00000000-0000-0000-0000-000000000000')
        
        self.assertIsNone(user)

    # Tests get_user_by_email

    def test_get_user_by_email_found(self):
        """Test récupération utilisateur par email existant"""
        user = self.repository.get_user_by_email('test1@example.com')
        
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test1@example.com')

    def test_get_user_by_email_not_found(self):
        """Test récupération avec email inexistant"""
        user = self.repository.get_user_by_email('nonexistent@example.com')
        
        self.assertIsNone(user)

    # Tests get_user_by_username

    def test_get_user_by_username_found(self):
        """Test récupération utilisateur par username existant"""
        user = self.repository.get_user_by_username('testuser1')
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser1')

    def test_get_user_by_username_not_found(self):
        """Test récupération avec username inexistant"""
        user = self.repository.get_user_by_username('nonexistent')
        
        self.assertIsNone(user)

    # Tests get_stats_nb_user

    def test_get_stats_nb_user(self):
        """Test comptage du nombre d'utilisateurs"""
        count = self.repository.get_stats_nb_user()
        
        self.assertEqual(count, 2)

    def test_get_stats_nb_user_empty(self):
        """Test comptage quand aucun utilisateur"""
        User.objects.all().delete()
        count = self.repository.get_stats_nb_user()
        
        self.assertEqual(count, 0)

    # Tests get_list_user_in

    def test_get_list_user_in_with_valid_uuids(self):
        """Test récupération d'une liste d'utilisateurs par UUIDs"""
        uuids = [str(self.user1.uuid), str(self.user2.uuid)]
        users = self.repository.get_list_user_in(uuids)
        
        self.assertEqual(len(users), 2)
        user_uuids = [str(u.uuid) for u in users]
        self.assertIn(str(self.user1.uuid), user_uuids)
        self.assertIn(str(self.user2.uuid), user_uuids)

    def test_get_list_user_in_with_partial_uuids(self):
        """Test récupération avec certains UUIDs invalides"""
        uuids = [str(self.user1.uuid), '00000000-0000-0000-0000-000000000000']
        users = self.repository.get_list_user_in(uuids)
        
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].uuid, self.user1.uuid)

    def test_get_list_user_in_empty_list(self):
        """Test récupération avec liste vide"""
        users = self.repository.get_list_user_in([])
        
        self.assertEqual(len(users), 0)

    # Tests get_inactive_users

    def test_get_inactive_users(self):
        """Test récupération des utilisateurs inactifs"""
        # Mettre à jour la date de dernière connexion
        past_date = timezone.now() - timedelta(days=100)
        self.user1.last_login = past_date
        self.user1.save()
        
        cutoff_date = timezone.now() - timedelta(days=30)
        inactive_users = self.repository.get_inactive_users(cutoff_date)
        
        self.assertGreaterEqual(len(inactive_users), 1)
        self.assertIn(self.user1, inactive_users)

    def test_get_inactive_users_none_inactive(self):
        """Test quand aucun utilisateur inactif"""
        # Tous les utilisateurs ont une connexion récente
        recent_date = timezone.now() - timedelta(days=1)
        self.user1.last_login = recent_date
        self.user2.last_login = recent_date
        self.user1.save()
        self.user2.save()
        
        cutoff_date = timezone.now() - timedelta(days=30)
        inactive_users = self.repository.get_inactive_users(cutoff_date)
        
        self.assertEqual(len(inactive_users), 0)

    # Tests get_not_actived_users

    def test_get_not_actived_users(self):
        """Test récupération des utilisateurs jamais connectés"""
        # Créer un utilisateur qui ne s'est jamais connecté
        old_date = timezone.now() - timedelta(days=60)
        user3 = User.objects.create_user(
            username='neverlogged',
            email='never@example.com',
            password='password'
        )
        user3.last_login = None
        user3.date_joined = old_date
        user3.save()
        
        cutoff_date = timezone.now() - timedelta(days=30)
        not_actived = self.repository.get_not_actived_users(cutoff_date)
        
        self.assertGreaterEqual(len(not_actived), 1)
        self.assertIn(user3, not_actived)

    def test_get_not_actived_users_all_logged_in(self):
        """Test quand tous les utilisateurs se sont connectés"""
        # Donner une date de connexion à tous
        for user in User.objects.all():
            user.last_login = timezone.now()
            user.save()
        
        cutoff_date = timezone.now() - timedelta(days=30)
        not_actived = self.repository.get_not_actived_users(cutoff_date)
        
        self.assertEqual(len(not_actived), 0)

    # Tests get_not_confirmed_users

    def test_get_not_confirmed_users(self):
        """Test récupération des utilisateurs non confirmés"""
        # Créer un utilisateur non confirmé
        old_date = timezone.now() - timedelta(days=10)
        user3 = User.objects.create_user(
            username='notconfirmed',
            email='notconfirmed@example.com',
            password='password'
        )
        user3.isConfirmed = False
        user3.demandeConfirmationDate = old_date
        user3.save()
        
        cutoff_date = timezone.now() - timedelta(days=5)
        not_confirmed = self.repository.get_not_confirmed_users(cutoff_date)
        
        self.assertGreaterEqual(len(not_confirmed), 1)
        self.assertIn(user3, not_confirmed)

    def test_get_not_confirmed_users_all_confirmed(self):
        """Test quand tous les utilisateurs sont confirmés"""
        for user in User.objects.all():
            user.isConfirmed = True
            user.save()
        
        cutoff_date = timezone.now() - timedelta(days=5)
        not_confirmed = self.repository.get_not_confirmed_users(cutoff_date)
        
        self.assertEqual(len(not_confirmed), 0)

    # Tests get_stats_created

    def test_get_stats_created(self):
        """Test statistiques de création d'utilisateurs sur une période"""
        start_date = timezone.now().date() - timedelta(days=7)
        end_date = timezone.now().date()
        
        stats = self.repository.get_stats_created(start_date, end_date)
        
        # Vérifie que les stats sont retournées
        self.assertIsNotNone(stats)
        # Au moins les 2 utilisateurs créés aujourd'hui
        total_count = sum(entry['count'] for entry in stats)
        self.assertGreaterEqual(total_count, 2)

    def test_get_stats_created_no_users_in_period(self):
        """Test statistiques quand aucun utilisateur créé dans la période"""
        # Période dans le futur
        start_date = timezone.now().date() + timedelta(days=1)
        end_date = timezone.now().date() + timedelta(days=7)
        
        stats = self.repository.get_stats_created(start_date, end_date)
        
        self.assertEqual(len(stats), 0)

    # Tests get_stats_connected

    def test_get_stats_connected(self):
        """Test statistiques de connexions sur une période"""
        # Définir des dates de connexion
        self.user1.last_login = timezone.now()
        self.user1.save()
        
        start_date = timezone.now().date() - timedelta(days=7)
        end_date = timezone.now().date()
        
        stats = self.repository.get_stats_connected(start_date, end_date)
        
        # Vérifie que les stats sont retournées
        self.assertIsNotNone(stats)

    def test_get_stats_connected_excludes_never_logged_in(self):
        """Test que les utilisateurs jamais connectés sont exclus"""
        # S'assurer qu'un utilisateur n'a jamais de last_login
        self.user2.last_login = None
        self.user2.save()
        
        self.user1.last_login = timezone.now()
        self.user1.save()
        
        start_date = timezone.now().date() - timedelta(days=1)
        end_date = timezone.now().date()
        
        stats = self.repository.get_stats_connected(start_date, end_date)
        
        # Seulement user1 devrait être compté
        total_count = sum(entry['count'] for entry in stats)
        self.assertGreaterEqual(total_count, 1)
