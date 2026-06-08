from __future__ import annotations

from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import gettext as _

from main.architecture.persistence.repository.SoundBoardRepository import SoundBoardRepository
from main.domain.common.utils.settings import Settings


class OnboardingContextService:
    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    def build_payload(self) -> dict:
        locale = self._resolve_locale()
        is_authenticated = bool(getattr(self.request.user, 'is_authenticated', False))

        payload = {
            'locale': locale,
            'labels': self._build_labels(),
            'urls': self._build_urls(is_authenticated),
            'steps': self._build_steps(is_authenticated),
            'feature_flags': {
                'onboarding_enabled': bool(Settings.get('ONBOARDING_ENABLED', True)),
            },
        }

        return payload

    def _resolve_locale(self) -> str:
        language = getattr(self.request, 'LANGUAGE_CODE', None) or get_language() or 'fr'
        return 'en' if str(language).startswith('en') else 'fr'

    def _build_labels(self) -> dict:
        return {
            'next': _('onboarding.labels.next'),
            'prev': _('onboarding.labels.prev'),
            'done': _('onboarding.labels.done'),
        }

    def _build_urls(self, is_authenticated: bool) -> dict:
        urls = {
            'home': reverse('home'),
            'login': reverse('login'),
        }

        if is_authenticated:
            urls.update(
                {
                    'dashboard': reverse('soundboardsList'),
                    'soundboardsNew': reverse('soundboardsNew'),
                    'settings': reverse('settingsIndex'),
                }
            )

        return urls

    def _build_steps(self, is_authenticated: bool) -> list[dict]:
        dynamic_url = self._create_dynamic_url()
        steps = [
            {
                'id': 'public_theme',
                'selector': '[data-shepherd="theme-toggle"]',
                'position': 'bottom',
                'title': _('onboarding.public.theme.title'),
                'description': _('onboarding.public.theme.description'),
                'redirect_url': reverse('home'),
            },
            {
                'id': 'public_fullscreen',
                'selector': '[data-shepherd="fullscreen-button"]',
                'position': 'bottom',
                'title': _('onboarding.public.fullscreen.title'),
                'description': _('onboarding.public.fullscreen.description'),
                'redirect_url': None,
            },
            {
                'id': 'public_soundboard',
                'selector': '[data-shepherd="public-soundboards-button"]',
                'position': 'bottom',
                'title': _('onboarding.public.soundboards.title'),
                'description': _('onboarding.public.soundboards.description'),
                'redirect_url': None,
            },
            {
                'id': 'public_soundboards',
                'selector': '[data-shepherd="public-soundboards-grid"]',
                'position': 'top',
                'title': _('onboarding.public.grid.title'),
                'description': _('onboarding.public.grid.description'),
                'redirect_url': reverse('publicListingSoundboard'),
            },
            {
                'id': 'private_soundboard_mixer',
                'selector': '[data-shepherd="soundboard-tracks"]',
                'position': 'top',
                'title': _('onboarding.private.tracks.title'),
                'description': _('onboarding.private.tracks.description'),
                'redirect_url': dynamic_url.get('public_soundboard'),
            },
            {
                'id': 'private_soundboard_mixer',
                'selector': '[data-shepherd="soundboard-mixer"]',
                'position': 'bottom',
                'title': _('onboarding.private.mixer.title'),
                'description': _('onboarding.private.mixer.description'),
                'redirect_url': None,
            },
        ]

        if is_authenticated:
            steps.extend(
                [
                    {
                        'id': 'private_my_soundboards',
                        'selector': '[data-shepherd="my-soundboards-button"]',
                        'position': 'top',
                        'title': _('onboarding.private.my_soundboards.title'),
                        'description': _('onboarding.private.my_soundboards.description'),
                        'redirect_url': None,
                    },
                    {
                        'id': 'private_my_soundboards',
                        'selector': '[data-shepherd="my-soundboards-grid"]',
                        'position': 'top',
                        'title': _('onboarding.private.my_soundboards_grid.title'),
                        'description': _('onboarding.private.my_soundboards_grid.description'),
                        'redirect_url': reverse('soundboardsList'),
                    },
                    {
                        'id': 'private_create_soundboard',
                        'selector': '[data-shepherd="create-soundboard-btn"]',
                        'position': 'bottom',
                        'title': _('onboarding.private.create_soundboard.title'),
                        'description': _('onboarding.private.create_soundboard.description'),
                        'redirect_url': None,
                    },
                    {
                        'id': 'private_playlist_button',
                        'selector': '[data-shepherd="my-playlist-button"]',
                        'position': 'bottom',
                        'title': _('onboarding.private.playlist_button.title'),
                        'description': _('onboarding.private.playlist_button.description'),
                        'redirect_url': None,
                    },
                    {
                        'id': 'private_copy_buttons',
                        'selector': '[data-shepherd="my-playlist-grid"]',
                        'position': 'bottom',
                        'title': _('onboarding.private.playlist_grid.title'),
                        'description': _('onboarding.private.playlist_grid.description'),
                        'redirect_url': reverse('playlistsAllList'),
                    },
                    {
                        'id': 'private_copy_buttons',
                        'selector': '[data-shepherd="copy-buttons-btn"]',
                        'position': 'top',
                        'title': _('onboarding.private.copiable_buttons.title'),
                        'description': _('onboarding.private.copiable_buttons.description'),
                        'redirect_url': None,
                    },
                    {
                        'id': 'private_copy_buttons',
                        'selector': '[data-shepherd="copy-buttons-grid"]',
                        'position': 'left',
                        'title': _('onboarding.private.copy_buttons_grid.title'),
                        'description': _('onboarding.private.copy_buttons_grid.description'),
                        'redirect_url': reverse('playlistsAllCopiableList'),
                    },
                    {
                        'id': 'private_user_settings',
                        'selector': '[data-shepherd="user-settings-link"]',
                        'position': 'left',
                        'title': _('onboarding.private.user_settings.title'),
                        'description': _('onboarding.private.user_settings.description'),
                        'redirect_url': reverse('settingsIndex'),
                    },
                ]
            )

        return steps

    def _create_dynamic_url(self) -> dict:
        soundboard = SoundBoardRepository().get_public_not_banned_with_min_tracks(minimum_tracks=5)
        if soundboard:
            public_soundboard = reverse('publicReadSoundboard', kwargs={'soundboard_uuid': soundboard.uuid})
        else:
            public_soundboard = None
        return {
            'public_soundboard': public_soundboard,
        }
