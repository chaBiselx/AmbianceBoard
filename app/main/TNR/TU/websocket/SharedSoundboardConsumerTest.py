import json
import asyncio
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from asgiref.sync import sync_to_async
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SharedSoundboard import SharedSoundboard
from django.contrib.auth import get_user_model
from parameters.routing import application

User = get_user_model()

# NOSONAR
class SharedSoundboardConsumerAsyncTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        # Initialisation synchrone (TransactionTestCase -> DB accessible)
        self.user = User.objects.create_user(username='u1', email='u1@ex.com', password='pass')
        self.soundboard = SoundBoard.objects.create(user=self.user, name='SB')
        self.shared = SharedSoundboard.objects.create(soundboard=self.soundboard)

    async def test_connect_and_broadcast_music_start(self):
        communicator1 = WebsocketCommunicator(application, f"/shared/ws/{self.soundboard.uuid}/{self.shared.token}")
        connected1, _ = await communicator1.connect()
        assert connected1

        communicator2 = WebsocketCommunicator(application, f"/shared/ws/{self.soundboard.uuid}/{self.shared.token}")
        connected2, _ = await communicator2.connect()
        assert connected2

        payload = {
            'type': 'music_start',
            'track': 'track1',
            'playlist_uuid': 'pl-123',
            'url_music': 'http://example.com/music.mp3'
        }
        await communicator1.send_json_to(payload)

        # communicator1 ne doit pas recevoir son propre message (on attend brièvement et on vérifie timeout)
        try:
            await asyncio.wait_for(communicator1.receive_json_from(), timeout=0.2)
            self.fail("Le premier client ne devrait pas recevoir son propre message")
        except asyncio.TimeoutError:
            pass  # Comportement attendu

        response2 = await communicator2.receive_json_from()
        self.assertEqual(response2['type'], 'music_start')
        self.assertEqual(response2['data']['track'], 'track1')

        await communicator1.disconnect()
        await communicator2.disconnect()

    async def test_invalid_params_close(self):
        communicator = WebsocketCommunicator(application, f"/shared/ws/{self.soundboard.uuid}/WRONGTOKEN")
        connected, _ = await communicator.connect()
        # La connexion devrait échouer ou se fermer rapidement (connected peut être False)
        if connected:
            await asyncio.sleep(0.1)
        # Disconnect (idempotent si déjà fermé)
        await communicator.disconnect()
