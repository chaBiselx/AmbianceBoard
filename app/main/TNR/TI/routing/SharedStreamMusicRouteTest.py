"""
Test d'intégration pour la route: Streaming de musique partagée (/shared/<uuid:soundboard_uuid>/<str:token>/<uuid:playlist_uuid>/<int:music_id>/stream)
"""
from django.test import TestCase, Client, RequestFactory, tag
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import get_user_model
from types import SimpleNamespace
from unittest.mock import Mock, patch
import uuid

from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from main.interface.ui.controller.sharedSoundboard import sharedViews
from main.interface.ui.controller.private import showSoundboardViews
from main.interface.ui.controller.public import publicViews

User = get_user_model()


@tag('integration')
class SharedStreamMusicRouteTest(TestCase):
    """Tests pour la route de streaming de musique partagée"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.test_uuid1 = uuid.uuid4()
        self.test_uuid2 = uuid.uuid4()
        self.test_token = "test-token-123"

    def test_missing_stream_results_return_404_without_logging_error(self):
        scenarios = [
            (False, None),
            (True, None),
            (True, 123),
        ]
        for metadata_only, cached_track_id in scenarios:
            with self.subTest(metadata_only=metadata_only, cached_track_id=cached_track_id):
                request = RequestFactory().get(
                    '/', HTTP_X_METADATA_ONLY='true' if metadata_only else 'false'
                )
                request.session = SimpleNamespace(session_key='test-session')
                with patch.object(sharedViews.CacheFactory, 'get_default_cache') as cache_factory, \
                     patch.object(sharedViews, 'TrackRepository') as track_repository, \
                     patch.object(sharedViews, 'RandomizeTrackService') as randomize_service, \
                     patch.object(sharedViews.logger, 'error') as log_error:
                    cache_factory.return_value.get.return_value = cached_track_id
                    track_repository.return_value.get.return_value = None
                    randomize_service.return_value.get_shared.return_value = None

                    response = sharedViews.shared_music_stream(
                        request, self.test_uuid1, self.test_uuid2, self.test_token, 1
                    )

                    self.assertEqual(response.status_code, 404)
                    self.assertEqual(response.content.decode(), ErrorMessageEnum.ELEMENT_NOT_FOUND.trad())
                    log_error.assert_not_called()
                    if metadata_only:
                        randomize_service.assert_not_called()
                        if cached_track_id is None:
                            track_repository.assert_not_called()

    def test_found_track_returns_stream_or_metadata(self):
        for metadata_only in (False, True):
            with self.subTest(metadata_only=metadata_only):
                request = RequestFactory().get(
                    '/', HTTP_X_METADATA_ONLY='true' if metadata_only else 'false'
                )
                request.session = SimpleNamespace(session_key='test-session')
                track = Mock(id=123)
                track.get_duration.return_value = 42
                track.get_reponse_content.return_value = HttpResponse(b'audio')
                with patch.object(sharedViews.CacheFactory, 'get_default_cache') as cache_factory, \
                     patch.object(sharedViews, 'TrackRepository') as track_repository, \
                     patch.object(sharedViews, 'RandomizeTrackService') as randomize_service:
                    cache_factory.return_value.get.return_value = track.id
                    track_repository.return_value.get.return_value = track
                    randomize_service.return_value.get_shared.return_value = track

                    response = sharedViews.shared_music_stream(
                        request, self.test_uuid1, self.test_uuid2, self.test_token, 1
                    )

                    self.assertEqual(response.status_code, 200)
                    cache_key = f'musicStream:test-session:{self.test_uuid1}:{self.test_uuid2}:specific:1'
                    if metadata_only:
                        self.assertJSONEqual(response.content, {'duration': 42})
                        cache_factory.return_value.get.assert_called_once_with(cache_key)
                        track_repository.return_value.get.assert_called_once_with(123, self.test_uuid2)
                        cache_factory.return_value.set.assert_not_called()
                    else:
                        self.assertIs(response, track.get_reponse_content.return_value)
                        cache_factory.return_value.set.assert_called_once_with(cache_key, 123, timeout=60)

    def test_range_request_reuses_the_randomly_selected_track(self):
        request = RequestFactory().get('/', HTTP_RANGE='bytes=20-')
        cached_track = Mock(id=123)

        for view_module, helper_name in (
            (showSoundboardViews, '_get_private_stream_track'),
            (publicViews, '_get_public_stream_track'),
        ):
            with self.subTest(view=view_module.__name__):
                cache = Mock()
                cache.get.return_value = cached_track.id
                with patch.object(view_module, 'TrackRepository') as track_repository, \
                     patch.object(view_module, 'RandomizeTrackService') as randomize_service:
                    track_repository.return_value.get.return_value = cached_track

                    track, is_new_track = getattr(view_module, helper_name)(
                        request,
                        cache,
                        'playback-cache-key',
                        self.test_uuid1,
                        self.test_uuid2,
                    )

                    self.assertIs(track, cached_track)
                    self.assertFalse(is_new_track)
                    track_repository.return_value.get.assert_called_once_with(123, self.test_uuid2)
                    randomize_service.assert_not_called()

    def test_specific_track_range_request_reuses_cached_track(self):
        request = RequestFactory().get('/', HTTP_RANGE='bytes=20-')
        cached_track = Mock(id=123)

        for view_module, helper_name in (
            (showSoundboardViews, '_get_private_specific_stream_track'),
            (publicViews, '_get_public_specific_stream_track'),
        ):
            with self.subTest(view=view_module.__name__):
                cache = Mock()
                cache.get.return_value = cached_track.id
                with patch.object(view_module, 'TrackRepository') as track_repository, \
                     patch.object(view_module, 'RandomizeTrackService') as randomize_service:
                    track_repository.return_value.get.return_value = cached_track

                    track, is_new_track = getattr(view_module, helper_name)(
                        request,
                        cache,
                        'playback-cache-key',
                        self.test_uuid1,
                        self.test_uuid2,
                        1,
                    )

                    self.assertIs(track, cached_track)
                    self.assertFalse(is_new_track)
                    track_repository.return_value.get.assert_called_once_with(123, self.test_uuid2)
                    randomize_service.assert_not_called()

    def test_range_header_is_forwarded_to_shared_track_response(self):
        request = RequestFactory().get('/', HTTP_RANGE='bytes=20-29')
        request.session = SimpleNamespace(session_key='test-session')
        track = Mock(id=123)
        track.get_reponse_content.return_value = HttpResponse(b'audio')

        with patch.object(sharedViews.CacheFactory, 'get_default_cache') as cache_factory, \
             patch.object(sharedViews, 'RandomizeTrackService') as randomize_service:
            randomize_service.return_value.get_shared.return_value = track

            response = sharedViews.shared_music_stream(
                request, self.test_uuid1, self.test_uuid2, self.test_token, 1
            )

        self.assertEqual(response.status_code, 200)
        track.get_reponse_content.assert_called_once_with('bytes=20-29')
    
    def test_shared_stream_music_accessible_without_auth(self):
        """Test que la route est accessible sans authentification"""
        response = self.client.get(
            reverse('sharedStreamMusic', kwargs={
                'soundboard_uuid': self.test_uuid1,
                'token': self.test_token,
                'playlist_uuid': self.test_uuid2,
                'music_id': 1
            })
        )
        self.assertIn(response.status_code, [200, 302, 404, 403])
    
    def test_shared_stream_music_with_invalid_token(self):
        """Test avec un token invalide"""
        response = self.client.get(
            reverse('sharedStreamMusic', kwargs={
                'soundboard_uuid': self.test_uuid1,
                'token': 'invalid-token',
                'playlist_uuid': self.test_uuid2,
                'music_id': 1
            })
        )
        self.assertIn(response.status_code, [404, 403])
    
    def test_shared_stream_music_with_invalid_uuids(self):
        """Test avec des UUIDs invalides"""
        response = self.client.get(
            reverse('sharedStreamMusic', kwargs={
                'soundboard_uuid': uuid.uuid4(),
                'token': self.test_token,
                'playlist_uuid': uuid.uuid4(),
                'music_id': 99999
            })
        )
        self.assertIn(response.status_code, [404, 403])
