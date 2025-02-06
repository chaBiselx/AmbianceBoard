import datetime
from django.test import TestCase
from home.models.User import User
from home.service.cron.RGPDService import RGPDService
from django.utils.timezone import make_aware

class RGPDServiceTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com')
        self.user1.last_login = make_aware(datetime.datetime.now() - datetime.timedelta(days=730))
        self.user1.save()

        self.user2 = User.objects.create_user(username='user2', email='user2@example.com')
        self.user2.last_login = make_aware(datetime.datetime.now() - datetime.timedelta(days=20))
        self.user2.save()

    def test_delete_inactive_users(self):
        RGPDService().delete_inactive_users()
        self.assertFalse(User.objects.filter(username='user1').exists())
        self.assertTrue(User.objects.filter(username='user2').exists())

    def test_prevent_inactive_users(self):
        RGPDService().prevent_inactive_users()
        self.assertTrue(User.objects.filter(username='user1').exists())
        self.assertTrue(User.objects.filter(username='user2').exists())
        
    def test_delete_inactive_users(self):
        # Créer des utilisateurs non actifs
        user1 = User.objects.create_user(username='userdeleted', email='user1@example.com')
        user1.last_login = datetime.datetime.now() - datetime.timedelta(days=365*2 + 1)
        user1.save()

        user2 = User.objects.create_user(username='userkeep', email='user2@example.com')
        user2.last_login = datetime.datetime.now() - datetime.timedelta(days=60)
        user2.save()

        # Appeler la méthode delete_inactive_users
        RGPDService().delete_inactive_users()

        # Vérifier que l'utilisateur non actif a été supprimé
        self.assertFalse(User.objects.filter(username='userdeleted').exists())
        self.assertTrue(User.objects.filter(username='userkeep').exists())
        
    def delete_not_active_users(self):
        # Créer des utilisateurs non actifs
        user1 = User.objects.create_user(username='userkeep', email='user1@example.com')
        user1.last_login = None
        user1.date_joined = datetime.datetime.now() - datetime.timedelta(days=365*2 + 1)
        user1.save()

        user2 = User.objects.create_user(username='userdeleted', email='user2@example.com')
        user2.save()
        
        # Appeler la méthode delete_not_active_users
        RGPDService().delete_not_active_users()
        
        # Vérifier que l'utilisateur non actif a été supprimé
        self.assertFalse(User.objects.filter(username='userdeleted').exists())
        self.assertTrue(User.objects.filter(username='userkeep').exists())

    def test_calculate_cutoff_date(self):
        service = RGPDService()
        cutoff_date = service._calculate_cuttoff_date(24)
        cutoff_date_obj = make_aware(datetime.datetime.now() - datetime.timedelta(days=24*30))
        self.assertAlmostEqual(cutoff_date.timestamp(), cutoff_date_obj.timestamp(), places=3)