"""
Test d'intégration pour les routes d'édition des scripts de soundboard.
"""
import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, tag
from django.urls import reverse

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.domain.common.enum.ScriptActionEnum import ScriptActionEnum
from main.domain.common.enum.ScriptTriggerEnum import ScriptTriggerEnum
from main.domain.common.service.script.SoundboardScriptService import SoundboardScriptService

User = get_user_model()


@tag('integration')
class SoundboardScriptRouteTest(TestCase):
    """Tests pour les routes de gestion des scripts"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='script-route-user',
            email='script-route@example.com',
            password='testpass123'
        )
        self.soundboard = SoundBoard.objects.create(user=self.user, name='SB scripts')
        self.playlist = Playlist.objects.create(name='Playlist route', user=self.user)
        SoundboardPlaylist.objects.create(SoundBoard=self.soundboard, Playlist=self.playlist, section=1, order=1)
        self.service = SoundboardScriptService(self.soundboard)
        self.client.login(username='script-route-user', password='testpass123')

    def test_page_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse('soundboardScripts', args=[self.soundboard.uuid]))
        self.assertIn(response.status_code, [302, 401, 403])

    def test_page_is_accessible_for_owner(self):
        response = self.client.get(reverse('soundboardScripts', args=[self.soundboard.uuid]))
        self.assertEqual(response.status_code, 200)

    def test_create_script(self):
        response = self.client.post(
            reverse('soundboardScriptCreate', args=[self.soundboard.uuid]),
            {'name': 'Ambiance taverne'}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.service.get_all()), 1)

    def test_create_script_requires_a_name(self):
        response = self.client.post(reverse('soundboardScriptCreate', args=[self.soundboard.uuid]), {'name': '  '})
        self.assertEqual(response.status_code, 400)

    def test_steps_fragment_is_rendered(self):
        script = self.service.create(name='Intro')
        response = self.client.get(
            reverse('soundboardScriptSteps', args=[self.soundboard.uuid, script.uuid])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'script-step-form')

    def test_save_step_collects_params_from_the_action_spec(self):
        script = self.service.create(name='Intro')
        response = self.client.post(
            reverse('soundboardScriptStepSave', args=[self.soundboard.uuid, script.uuid]),
            {
                'action_type': ScriptActionEnum.SET_VOLUME.name,
                'trigger_type': ScriptTriggerEnum.TIMECODE.name,
                'trigger_offset_ms': '1500',
                'playlist_uuid': str(self.playlist.uuid),
                'volume': '40',
            }
        )
        self.assertEqual(response.status_code, 200)

        step = self.service.step_repository.get_all(script)[0]
        self.assertEqual(step.params, {'playlist_uuid': str(self.playlist.uuid), 'volume': 40})
        self.assertEqual(step.trigger_offset_ms, 1500)

    def test_save_step_returns_error_on_invalid_params(self):
        script = self.service.create(name='Intro')
        response = self.client.post(
            reverse('soundboardScriptStepSave', args=[self.soundboard.uuid, script.uuid]),
            {
                'action_type': ScriptActionEnum.SET_VOLUME.name,
                'trigger_type': ScriptTriggerEnum.IMMEDIATE.name,
                'playlist_uuid': str(self.playlist.uuid),
                'volume': '400',
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_step(self):
        script = self.service.create(name='Intro')
        step = self.__add_step(script)

        response = self.client.delete(
            reverse('soundboardScriptStepDelete', args=[self.soundboard.uuid, script.uuid, step.uuid])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.service.step_repository.get_all(script), [])

    def test_reorder_steps(self):
        script = self.service.create(name='Intro')
        first = self.__add_step(script)
        second = self.__add_step(script)

        response = self.client.post(
            reverse('soundboardScriptStepsReorder', args=[self.soundboard.uuid, script.uuid]),
            data=json.dumps({'steps': [str(second.uuid), str(first.uuid)]}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [step.uuid for step in self.service.step_repository.get_all(script)],
            [second.uuid, first.uuid]
        )

    def test_delete_script(self):
        script = self.service.create(name='Intro')
        response = self.client.delete(
            reverse('soundboardScriptDelete', args=[self.soundboard.uuid, script.uuid])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.service.get_all(), [])

    def test_update_script_toggles_enabled(self):
        script = self.service.create(name='Intro')
        response = self.client.post(
            reverse('soundboardScriptUpdate', args=[self.soundboard.uuid, script.uuid]),
            {'enabled': 'false'}
        )
        self.assertEqual(response.status_code, 200)
        script.refresh_from_db()
        self.assertFalse(script.enabled)

    def test_routes_reject_a_soundboard_from_another_user(self):
        other_user = User.objects.create_user(
            username='script-route-other', email='other@example.com', password='testpass123'
        )
        other_soundboard = SoundBoard.objects.create(user=other_user, name='SB other')

        response = self.client.post(
            reverse('soundboardScriptCreate', args=[other_soundboard.uuid]), {'name': 'Hack'}
        )

        self.assertEqual(response.status_code, 404)

    def __add_step(self, script):
        return self.service.add_step(
            script,
            action_type=ScriptActionEnum.PLAY_PLAYLIST.name,
            trigger_type=ScriptTriggerEnum.IMMEDIATE.name,
            params={'playlist_uuid': str(self.playlist.uuid)},
        )
