"""
Tests pour le middleware ErrorTrackingMiddleware.

Tests unitaires pour vérifier le bon fonctionnement du middleware
de traçage des erreurs HTTP.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, Http404
from main.middleware.ErrorTrackingMiddleware import ErrorTrackingMiddleware
from main.models.User import User
from main.models.UserActivity import UserActivity
from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum


class ErrorTrackingMiddlewareTest(TestCase):
    """Tests pour le middleware ErrorTrackingMiddleware."""
    
    def setUp(self):
        """Configuration initiale des tests."""
        self.factory = RequestFactory()
        self.get_response_mock = Mock()
        self.middleware = ErrorTrackingMiddleware(self.get_response_mock)
        
        # Créer un utilisateur de test
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_middleware_initialization(self):
        """Test de l'initialisation du middleware."""
        self.assertIsNotNone(self.middleware.get_response)
        self.assertIsNotNone(self.middleware.logger)
        self.assertIsNotNone(self.middleware.error_mapping)

    def test_error_404_tracking_authenticated_user(self):
        """Test du traçage d'une erreur 404 pour un utilisateur connecté."""
        # Préparer la requête
        request = self.factory.get('/nonexistent-page/')
        request.user = self.test_user
        request.session = MagicMock()
        request.session.session_key = 'test_session_key'
        
        # Préparer la réponse avec erreur 404
        self.get_response_mock.return_value = HttpResponse(status=404)
        
        # Exécuter le middleware
        self.middleware(request)
        
        # Vérifier que l'activité a été créée
        activities = UserActivity.objects.filter(
            user=self.test_user,
            activity_type=UserActivityTypeEnum.ERROR_404.value
        )
        self.assertEqual(activities.count(), 1)
        
        # Vérifier les détails de l'activité
        activity = activities.first()
        self.assertEqual(activity.user, self.test_user)
        self.assertTrue(activity.is_authenticated)
        self.assertEqual(activity.activity_type, UserActivityTypeEnum.ERROR_404.value)

    def test_error_500_tracking_anonymous_user(self):
        """Test du traçage d'une erreur 500 pour un utilisateur anonyme."""
        # Préparer la requête
        request = self.factory.get('/error-page/')
        request.user = AnonymousUser()
        request.session = MagicMock()
        request.session.session_key = 'anonymous_session'
        
        # Préparer la réponse avec erreur 500
        self.get_response_mock.return_value = HttpResponse(status=500)
        
        # Exécuter le middleware
        self.middleware(request)
        
        # Vérifier que l'activité a été créée
        activities = UserActivity.objects.filter(
            activity_type=UserActivityTypeEnum.ERROR_500.value,
            session_key='anonymous_session'
        )
        self.assertEqual(activities.count(), 1)
        
        # Vérifier les détails de l'activité
        activity = activities.first()
        self.assertIsNone(activity.user)
        self.assertFalse(activity.is_authenticated)
        self.assertEqual(activity.session_key, 'anonymous_session')

    def test_error_4xx_generic_tracking(self):
        """Test du traçage d'une erreur 4XX générique."""
        # Préparer la requête
        request = self.factory.get('/forbidden-page/')
        request.user = self.test_user
        request.session = MagicMock()
        request.session.session_key = 'test_session'
        
        # Préparer la réponse avec erreur 403
        self.get_response_mock.return_value = HttpResponse(status=403)
        
        # Exécuter le middleware
        self.middleware(request)
        
        # Vérifier que l'activité 4XX générique a été créée
        activities = UserActivity.objects.filter(
            user=self.test_user,
            activity_type=UserActivityTypeEnum.ERROR_4XX.value
        )
        self.assertEqual(activities.count(), 1)

    def test_error_5xx_generic_tracking(self):
        """Test du traçage d'une erreur 5XX générique."""
        # Préparer la requête
        request = self.factory.get('/server-error/')
        request.user = self.test_user
        request.session = MagicMock()
        request.session.session_key = 'test_session'
        
        # Préparer la réponse avec erreur 502
        self.get_response_mock.return_value = HttpResponse(status=502)
        
        # Exécuter le middleware
        self.middleware(request)
        
        # Vérifier que l'activité 5XX générique a été créée
        activities = UserActivity.objects.filter(
            user=self.test_user,
            activity_type=UserActivityTypeEnum.ERROR_5XX.value
        )
        self.assertEqual(activities.count(), 1)

    def test_success_response_no_tracking(self):
        """Test qu'aucun traçage n'est effectué pour les réponses de succès."""
        # Préparer la requête
        request = self.factory.get('/success-page/')
        request.user = self.test_user
        request.session = MagicMock()
        request.session.session_key = 'test_session'
        
        # Préparer la réponse de succès
        self.get_response_mock.return_value = HttpResponse(status=200)
        
        # Exécuter le middleware
        self.middleware(request)
        
        # Vérifier qu'aucune activité d'erreur n'a été créée
        error_activities = UserActivity.objects.filter(
            user=self.test_user,
            activity_type__startswith='error_'
        )
        self.assertEqual(error_activities.count(), 0)

    def test_specific_error_codes_mapping(self):
        """Test du mapping des codes d'erreur spécifiques."""
        specific_errors = [
            (404, UserActivityTypeEnum.ERROR_404),
            (405, UserActivityTypeEnum.ERROR_405),
            (406, UserActivityTypeEnum.ERROR_406),
            (429, UserActivityTypeEnum.ERROR_429),
            (500, UserActivityTypeEnum.ERROR_500),
        ]
        
        for status_code, expected_activity_type in specific_errors:
            with self.subTest(status_code=status_code):
                # Nettoyer les activités précédentes
                UserActivity.objects.all().delete()
                
                # Préparer la requête
                request = self.factory.get(f'/error-{status_code}/')
                request.user = self.test_user
                request.session = MagicMock()
                request.session.session_key = 'test_session'
                
                # Préparer la réponse avec le code d'erreur
                self.get_response_mock.return_value = HttpResponse(status=status_code)
                
                # Exécuter le middleware
                self.middleware(request)
                
                # Vérifier que l'activité correcte a été créée
                activities = UserActivity.objects.filter(
                    user=self.test_user,
                    activity_type=expected_activity_type.value
                )
                self.assertEqual(activities.count(), 1)

    def test_exception_handling_during_tracking(self):
        """Test de la gestion des exceptions lors du traçage."""
        # Préparer la requête
        request = self.factory.get('/error-page/')
        request.user = self.test_user
        request.session = MagicMock()
        request.session.session_key = 'test_session'

        # Préparer la réponse avec erreur
        self.get_response_mock.return_value = HttpResponse(status=404)

        # Simuler une exception lors de la création d'activité
        with patch.object(self.middleware, 'logger') as mock_logger:
            with patch('main.models.UserActivity.UserActivity.create_activity') as mock_create:
                mock_create.side_effect = Exception("Database error")

                # Exécuter le middleware - ne doit pas lever d'exception
                response = self.middleware(request)

                # Vérifier que l'erreur a été loggée
                mock_logger.error.assert_called()

                # Vérifier que la réponse est toujours retournée
                self.assertEqual(response.status_code, 404)

    def test_excluded_urls_not_tracked(self):
        """Test que les URLs exclues ne sont pas tracées."""
        excluded_urls = [
            '/.well-known/appspecific/com.chrome.devtools.json',
            '/.well-known/security.txt',
            '/favicon.ico',
            '/robots.txt',
            '/sitemap.xml',
            '/apple-touch-icon-120x120.png',
            '/.env',
            '/wp-admin/login.php',
            '/config.php',
            '/ads.txt',
        ]
        
        for url in excluded_urls:
            with self.subTest(url=url):
                # Nettoyer les activités précédentes
                UserActivity.objects.all().delete()
                
                # Préparer la requête pour une URL exclue
                request = self.factory.get(url)
                request.user = self.test_user
                request.session = MagicMock()
                request.session.session_key = 'test_session'
                
                # Préparer la réponse avec erreur 404
                self.get_response_mock.return_value = HttpResponse(status=404)
                
                # Exécuter le middleware
                self.middleware(request)
                
                # Vérifier qu'aucune activité d'erreur n'a été créée
                activities = UserActivity.objects.filter(
                    activity_type__startswith='error_'
                )
                self.assertEqual(activities.count(), 0, f"URL {url} ne devrait pas être tracée")

    def test_application_urls_still_tracked(self):
        """Test que les URLs de l'application sont toujours tracées."""
        application_urls = [
            '/dashboard/',
            '/soundboard/123/',
            '/playlist/456/',
            '/user/profile/',
            '/api/music/upload/',
            '/static/css/style.css',  # Même les ressources statiques peuvent être tracées
        ]
        
        for url in application_urls:
            with self.subTest(url=url):
                # Nettoyer les activités précédentes
                UserActivity.objects.all().delete()
                
                # Préparer la requête
                request = self.factory.get(url)
                request.user = self.test_user
                request.session = MagicMock()
                request.session.session_key = 'test_session'
                
                # Préparer la réponse avec erreur 404
                self.get_response_mock.return_value = HttpResponse(status=404)
                
                # Exécuter le middleware
                self.middleware(request)
                
                # Vérifier qu'une activité d'erreur a été créée
                activities = UserActivity.objects.filter(
                    user=self.test_user,
                    activity_type=UserActivityTypeEnum.ERROR_404.value
                )
                self.assertEqual(activities.count(), 1, f"URL {url} devrait être tracée")

    def test_should_exclude_url_method(self):
        """Test de la méthode _should_exclude_url."""
        test_cases = [
            # URLs à exclure
            ('/.well-known/appspecific/com.chrome.devtools.json', True),
            ('/.well-known/security.txt', True),
            ('/favicon.ico', True),
            ('/wp-admin/login.php', True),
            ('/.git/config', True),
            ('/phpmyadmin/index.php', True),
            
            # URLs à ne pas exclure
            ('/dashboard/', False),
            ('/api/soundboard/', False),
            ('/user/login/', False),
            ('/static/css/main.css', False),
            ('/media/uploads/song.mp3', False),
        ]
        
        for url, should_exclude in test_cases:
            with self.subTest(url=url):
                request = self.factory.get(url)
                result = self.middleware._should_exclude_url(request)
                self.assertEqual(result, should_exclude, 
                               f"URL {url} - Expected exclusion: {should_exclude}, got: {result}")


if __name__ == '__main__':
    unittest.main()
