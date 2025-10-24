"""
Tests pour le middleware DailySessionMiddleware.

Vérifie le bon fonctionnement de la gestion des sessions quotidiennes 
et de la mise à jour du champ last_login.
"""

from django.test import TestCase, RequestFactory, tag
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils import timezone
from unittest.mock import patch
import datetime

from main.architecture.middleware.DailySessionMiddleware import DailySessionMiddleware

User = get_user_model()


@tag('unitaire')
class DailySessionMiddlewareTest(TestCase):
    """Tests pour DailySessionMiddleware."""
    
    def setUp(self):
        """Configuration initiale des tests."""
        self.factory = RequestFactory()
        self.middleware = DailySessionMiddleware(lambda r: None)
        
        # Créer un utilisateur test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def _get_request_with_session(self, user=None):
        """
        Crée une requête avec session configurée.
        
        Args:
            user: Utilisateur à authentifier (optionnel)
            
        Returns:
            HttpRequest: Requête avec session
        """
        request = self.factory.get('/')
        
        # Ajouter le middleware de session
        session_middleware = SessionMiddleware(lambda r: None)
        session_middleware.process_request(request)
        request.session.save()
        
        # Authentifier l'utilisateur si fourni
        if user:
            request.user = user
        else:
            # Simuler un utilisateur anonyme
            from django.contrib.auth.models import AnonymousUser
            request.user = AnonymousUser()
            
        return request
    
    def test_middleware_with_anonymous_user(self):
        """Test que le middleware n'affecte pas les utilisateurs anonymes."""
        request = self._get_request_with_session()
        
        # Le middleware ne doit rien faire pour un utilisateur anonyme
        # Utiliser __call__ au lieu de _process_daily_session directement
        self.middleware(request)
        
        # Aucune clé de session ne doit être créée
        self.assertNotIn(DailySessionMiddleware.SESSION_DATE_KEY, request.session)
    
    def test_first_daily_session(self):
        """Test de la première session quotidienne d'un utilisateur."""
        request = self._get_request_with_session(self.user)
        original_last_login = self.user.last_login
        
        # Traiter la session
        self.middleware._process_daily_session(request)
        
        # Vérifier que la date de session est enregistrée
        self.assertIn(DailySessionMiddleware.SESSION_DATE_KEY, request.session)
        
        current_date = timezone.now().date()
        session_date_str = request.session[DailySessionMiddleware.SESSION_DATE_KEY]
        self.assertEqual(session_date_str, current_date.strftime('%Y-%m-%d'))
        
        # Vérifier que last_login a été mis à jour
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.last_login, original_last_login)
        self.assertIsNotNone(self.user.last_login)
    
    def test_same_day_session(self):
        """Test qu'une session le même jour ne met pas à jour last_login."""
        request = self._get_request_with_session(self.user)
        current_date = timezone.now().date()
        
        # Simuler une session existante du même jour
        request.session[DailySessionMiddleware.SESSION_DATE_KEY] = current_date.strftime('%Y-%m-%d')
        
        # Mettre à jour last_login pour le test
        test_last_login = timezone.now()
        User.objects.filter(pk=self.user.pk).update(last_login=test_last_login)
        self.user.refresh_from_db()
        
        # Traiter la session
        self.middleware._process_daily_session(request)
        
        # Vérifier que last_login n'a pas été modifié
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.last_login.replace(microsecond=0),
            test_last_login.replace(microsecond=0)
        )
    
    def test_different_day_session(self):
        """Test qu'une session d'un jour différent met à jour last_login."""
        request = self._get_request_with_session(self.user)
        
        # Simuler une session d'hier
        yesterday = timezone.now().date() - datetime.timedelta(days=1)
        request.session[DailySessionMiddleware.SESSION_DATE_KEY] = yesterday.strftime('%Y-%m-%d')
        
        # Mettre à jour last_login avec une date antérieure
        old_last_login = timezone.now() - datetime.timedelta(days=2)
        User.objects.filter(pk=self.user.pk).update(last_login=old_last_login)
        
        # Traiter la session
        self.middleware._process_daily_session(request)
        
        # Vérifier que last_login a été mis à jour
        self.user.refresh_from_db()
        self.assertGreater(self.user.last_login, old_last_login)
        
        # Vérifier que la session a été mise à jour avec la date actuelle
        current_date = timezone.now().date()
        session_date_str = request.session[DailySessionMiddleware.SESSION_DATE_KEY]
        self.assertEqual(session_date_str, current_date.strftime('%Y-%m-%d'))
    
    def test_invalid_session_date_format(self):
        """Test le comportement avec un format de date de session invalide."""
        request = self._get_request_with_session(self.user)
        
        # Simuler un format de date invalide
        request.session[DailySessionMiddleware.SESSION_DATE_KEY] = 'invalid-date'
        
        original_last_login = self.user.last_login
        
        # Traiter la session (ne doit pas lever d'exception)
        self.middleware._process_daily_session(request)
        
        # Vérifier que la session a été corrigée avec la date actuelle
        current_date = timezone.now().date()
        session_date_str = request.session[DailySessionMiddleware.SESSION_DATE_KEY]
        self.assertEqual(session_date_str, current_date.strftime('%Y-%m-%d'))
        
        # Vérifier que last_login a été mis à jour
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.last_login, original_last_login)
    
    def test_middleware_handles_exceptions(self):
        """Test que le middleware gère gracieusement les exceptions."""
        request = self._get_request_with_session(self.user)
        
        # Tester qu'aucune exception n'est levée même avec des données corrompues
        try:
            self.middleware(request)
            # Si on arrive ici, c'est que le middleware n'a pas levé d'exception
            # Ce qui est le comportement attendu
            test_passed = True
        except Exception:
            test_passed = False
            
        self.assertTrue(test_passed, "Le middleware doit gérer les exceptions gracieusement")