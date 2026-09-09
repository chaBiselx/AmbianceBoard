from django.test import TestCase, tag

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.User import User
from main.domain.common.enum.ScriptActionEnum import ScriptActionEnum
from main.domain.common.enum.ScriptTriggerEnum import ScriptTriggerEnum
from main.domain.common.exceptions.SoundboardScriptException import InvalidScriptStepException
from main.domain.common.service.script.SoundboardScriptSerializer import SoundboardScriptSerializer
from main.domain.common.service.script.SoundboardScriptService import SoundboardScriptService


@tag('unitaire')
class SoundboardScriptServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='soundboard-script-service-user',
            email='soundboard-script-service@test.com',
            password='testpass123'
        )
        self.soundboard = SoundBoard.objects.create(user=self.user, name='SB script test')
        self.playlist = Playlist.objects.create(name='Playlist script', user=self.user)
        SoundboardPlaylist.objects.create(SoundBoard=self.soundboard, Playlist=self.playlist, section=1, order=1)

        self.other_soundboard = SoundBoard.objects.create(user=self.user, name='SB other')
        self.foreign_playlist = Playlist.objects.create(name='Playlist foreign', user=self.user)
        SoundboardPlaylist.objects.create(
            SoundBoard=self.other_soundboard, Playlist=self.foreign_playlist, section=1, order=1
        )

        self.service = SoundboardScriptService(self.soundboard)
        self.script = self.service.create(name='Intro')

    def test_create_increments_order(self):
        second = self.service.create(name='Combat')
        self.assertEqual(self.script.order, 0)
        self.assertEqual(second.order, 1)

    def test_add_step_keeps_only_declared_params(self):
        step = self.service.add_step(
            self.script,
            action_type=ScriptActionEnum.PLAY_PLAYLIST.name,
            trigger_type=ScriptTriggerEnum.IMMEDIATE.name,
            params={'playlist_uuid': str(self.playlist.uuid), 'unexpected': 'value'},
        )
        self.assertEqual(step.params, {'playlist_uuid': str(self.playlist.uuid)})

    def test_add_step_rejects_playlist_outside_soundboard(self):
        with self.assertRaises(InvalidScriptStepException):
            self.service.add_step(
                self.script,
                action_type=ScriptActionEnum.PLAY_PLAYLIST.name,
                trigger_type=ScriptTriggerEnum.IMMEDIATE.name,
                params={'playlist_uuid': str(self.foreign_playlist.uuid)},
            )

    def test_add_step_rejects_unknown_action(self):
        with self.assertRaises(InvalidScriptStepException):
            self.service.add_step(
                self.script,
                action_type='UNKNOWN_ACTION',
                trigger_type=ScriptTriggerEnum.IMMEDIATE.name,
                params={'playlist_uuid': str(self.playlist.uuid)},
            )

    def test_add_step_rejects_on_step_end_without_source(self):
        with self.assertRaises(InvalidScriptStepException):
            self.service.add_step(
                self.script,
                action_type=ScriptActionEnum.PLAY_PLAYLIST.name,
                trigger_type=ScriptTriggerEnum.ON_STEP_END.name,
                params={'playlist_uuid': str(self.playlist.uuid)},
            )

    def test_add_step_rejects_out_of_range_volume(self):
        with self.assertRaises(InvalidScriptStepException):
            self.service.add_step(
                self.script,
                action_type=ScriptActionEnum.SET_VOLUME.name,
                trigger_type=ScriptTriggerEnum.IMMEDIATE.name,
                params={'playlist_uuid': str(self.playlist.uuid), 'volume': 150},
            )

    def test_add_step_links_source_step(self):
        first = self.__add_play_step()
        second = self.service.add_step(
            self.script,
            action_type=ScriptActionEnum.STOP_PLAYLIST.name,
            trigger_type=ScriptTriggerEnum.ON_STEP_END.name,
            params={'playlist_uuid': str(self.playlist.uuid)},
            trigger_offset_ms=500,
            trigger_source_step_uuid=str(first.uuid),
        )
        self.assertEqual(second.trigger_source_step, first)
        self.assertEqual(second.trigger_offset_ms, 500)

    def test_reorder_steps(self):
        first = self.__add_play_step()
        second = self.__add_play_step()

        self.service.reorder_steps(self.script, [str(second.uuid), str(first.uuid)])

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(second.order, 0)
        self.assertEqual(first.order, 1)

    def test_serializer_exposes_steps_with_source_uuid(self):
        first = self.__add_play_step()
        self.service.add_step(
            self.script,
            action_type=ScriptActionEnum.STOP_PLAYLIST.name,
            trigger_type=ScriptTriggerEnum.ON_STEP_END.name,
            params={'playlist_uuid': str(self.playlist.uuid)},
            trigger_source_step_uuid=str(first.uuid),
        )

        payload = SoundboardScriptSerializer.serialize_many(self.service.get_all_enabled())

        self.assertEqual(len(payload), 1)
        self.assertEqual(len(payload[0]['steps']), 2)
        self.assertIsNone(payload[0]['steps'][0]['trigger_source_step_uuid'])
        self.assertEqual(payload[0]['steps'][1]['trigger_source_step_uuid'], str(first.uuid))

    def test_get_all_enabled_excludes_disabled_scripts(self):
        self.service.update(self.script, enabled=False)
        self.assertEqual(self.service.get_all_enabled(), [])
        self.assertEqual(len(self.service.get_all()), 1)

    def __add_play_step(self):
        return self.service.add_step(
            self.script,
            action_type=ScriptActionEnum.PLAY_PLAYLIST.name,
            trigger_type=ScriptTriggerEnum.IMMEDIATE.name,
            params={'playlist_uuid': str(self.playlist.uuid)},
        )
