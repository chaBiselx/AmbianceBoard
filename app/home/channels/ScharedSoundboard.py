import logging
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger('home')

class ScharedSoundboard(AsyncWebsocketConsumer):
    async def connect(self):
        # Récupération des paramètres d'URL
        self.soundboard_uuid = self.scope['url_route']['kwargs']['soundboard_uuid']
        self.token = self.scope['url_route']['kwargs']['token']
        
        # Validation des paramètres
        if not await self.validate_connection():
            await self.close(code=4000)  # Code d'erreur personnalisé
            return
        
        # Création du nom de groupe dynamique
        self.group_name = f"soundboard_{self.soundboard_uuid}_{self.token}"
        
        # Ajout au groupe
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()


    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'music_start':
                await self.handle_music_start(data)
            elif message_type == 'music_stop':
                await self.handle_music_stop(data)
            elif message_type == 'music_stop_all':
                await self.handle_music_stop_all(data)
            else:
                # Echo pour les autres messages
                await self.send(text_data=json.dumps({
                    'type': 'echo',
                    'data': data
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Format JSON invalide',
                'data': text_data
            }))

    async def handle_music_start(self, data):
        """Gère le démarrage de musique"""
        
        track = data.get('track')
        playlist_uuid = data.get('playlist_uuid')
        url_music = data.get('url_music')
        if not track:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Track manquant'
            }))
            return
        if not playlist_uuid:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'playlist_uuid manquant'
            }))
            return
        if not url_music:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'url_music manquant'
            }))
            return
            
        # Diffuser à tout le groupe
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'music_start',
                'track': track,
                'playlist_uuid': playlist_uuid,
                'url_music': url_music,
                'sender': self.channel_name
            }
        )

    async def handle_music_stop(self, data):
        """Gère l'arrêt de musique"""
        playlist_uuid = data.get('playlist_uuid')
        if not playlist_uuid:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'playlist_uuid manquant'
            }))
            return
        
        # Diffuser à tout le groupe
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'music_stop',
                'track': track,
                'playlist_uuid': playlist_uuid,
                'sender': self.channel_name
            }
        )
        
    async def handle_music_stop_all(self, data):
        """Gère l'arrêt de musique"""
        # Diffuser à tout le groupe
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'music_stop_all',
                'track': None,
                'playlist_uuid': None,
                'sender': self.channel_name
            }
        )

    # Handlers pour les messages du groupe
    async def music_start(self, event):
        """Reçoit les messages music_start du groupe"""
        # Ne pas renvoyer le message à l'expéditeur
        if event.get('sender') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'music_start',
                'data' : {
                    'track': event['track'],
                    'playlist_uuid': event['playlist_uuid'],
                    'url_music': event.get('url_music', ''), 
                }
            }))

    async def music_stop(self, event):
        """Reçoit les messages music_stop du groupe"""
        # Ne pas renvoyer le message à l'expéditeur
        if event.get('sender') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'music_stop',
                'data': {
                    'track': event.get('track', None),
                    'playlist_uuid': event['playlist_uuid'],
                    'url_music': event.get('url_music', None),
                }
            }))
            
    async def music_stop_all(self, event):
        """Reçoit les messages music_stop_all du groupe"""
        # Ne pas renvoyer le message à l'expéditeur
        if event.get('sender') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'music_stop_all'
            }))
        
    async def validate_connection(self):
        """Valide la connexion avec UUID et token"""
        try:
            # Import du modèle uniquement quand nécessaire
            shared_soundboard = await self._get_shared_soundboard()
            
            if shared_soundboard is None:
                logger.error(f"Soundboard introuvable: {self.soundboard_uuid}")
                return False
                
            logger.info(f"Connexion validée pour soundboard: {self.soundboard_uuid}")
            return True
            
        except Exception as e:
            logger.error(f" Erreur validation: {e}")
            return False
        
    @database_sync_to_async
    def _get_shared_soundboard(self):
        """Récupère le SharedSoundboard de manière asynchrone"""
        try:
            
            # Import local pour éviter le problème AppRegistryNotReady
            from home.models.SharedSoundboard import SharedSoundboard
            from home.models.SoundBoard import SoundBoard
            
            soundboard = SoundBoard.objects.get(uuid=self.soundboard_uuid)
            if not soundboard:
                return None
            #TODO use CACHE
            
            return SharedSoundboard.objects.get(
                soundboard=soundboard, 
                token=self.token
            )
        except SharedSoundboard.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du soundboard: {e}")
            return None
