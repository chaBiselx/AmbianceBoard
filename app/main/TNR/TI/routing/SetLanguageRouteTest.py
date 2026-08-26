"""
Test d'intégration pour la route: set-language (/set-language/)
"""
from django.conf import settings
from django.test import TestCase, Client, tag
from django.urls import reverse


@tag('integration')
class SetLanguageRouteTest(TestCase):
    """Tests pour la route set_language en fonction de la langue de l'utilisateur"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('set_language')

    def test_set_language_francophone_user_sets_fr(self):
        """Un utilisateur francophone doit obtenir la langue fr"""
        response = self.client.post(self.url, {'language': 'fr', 'next': '/'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.cookies[settings.LANGUAGE_COOKIE_NAME].value, 'fr')

    def test_set_language_non_francophone_user_sets_en(self):
        """Un utilisateur non francophone doit obtenir la langue en"""
        response = self.client.post(self.url, {'language': 'en', 'next': '/'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.cookies[settings.LANGUAGE_COOKIE_NAME].value, 'en')

    def test_set_language_redirects_to_next(self):
        """La route doit rediriger vers le paramètre next fourni"""
        response = self.client.post(self.url, {'language': 'en', 'next': '/pricing'})

        self.assertRedirects(response, '/pricing', fetch_redirect_response=False)

    def test_set_language_persists_across_requests(self):
        """La langue choisie doit être conservée sur la requête suivante"""
        self.client.post(self.url, {'language': 'en', 'next': '/'})

        response = self.client.get(reverse('home'))

        self.assertEqual(self.client.cookies[settings.LANGUAGE_COOKIE_NAME].value, 'en')
        self.assertEqual(response.status_code, 200)

    def test_browser_language_francophone_activates_fr(self):
        """Un navigateur envoyant une préférence francophone doit activer le fr"""
        response = self.client.get(reverse('home'), HTTP_ACCEPT_LANGUAGE='fr-FR,fr;q=0.9')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Content-Language'), 'fr')

    def test_browser_language_francophone_belge_activates_fr(self):
        """Un navigateur envoyant une préférence francophone belge (fr-BE) doit activer le fr"""
        response = self.client.get(reverse('home'), HTTP_ACCEPT_LANGUAGE='fr-BE,fr;q=0.9')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Content-Language'), 'fr')

    def test_browser_language_non_francophone_activates_en(self):
        """Un navigateur envoyant une préférence non francophone (mais supportée) doit activer le en"""
        response = self.client.get(reverse('home'), HTTP_ACCEPT_LANGUAGE='en-US,en;q=0.9')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Content-Language'), 'en')

    def test_browser_language_unsupported_falls_back_to_default(self):
        """Une langue de navigateur non supportée (ni fr ni en) doit retomber sur LANGUAGE_CODE"""
        response = self.client.get(reverse('home'), HTTP_ACCEPT_LANGUAGE='de-DE,de;q=0.9')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Content-Language'), settings.LANGUAGE_CODE)
