import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from main.domain.common.utils.cache.CacheFactory import CacheFactory
from main.domain.common.utils.settings import Settings
from main.domain.common.utils.logger import logger

class SharedSoundboardConsummers(AsyncWebsocketConsumer):
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
            elif message_type == 'send_mixer_update':
                await self.handle_mixer_update(data)
            elif message_type == 'send_playlist_update_volume':
                await self.handle_playlist_update_volume(data)
                
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

    async def _check_missing_params(self, data, params):
        """Vérifie les paramètres manquants et envoie une erreur si nécessaire."""
        for param in params:
            # cas pour le volume ou une valeur peut être 0
            if param == 'volume' or param == 'value':
                if data.get(param) is None:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': f'{param} manquant'
                    }))
                    return True
            elif not data.get(param):
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'{param} manquant'
                }))
                return True
        return False

    async def handle_music_start(self, data):
        """Gère le démarrage de musique"""
        
        if await self._check_missing_params(data, ['track', 'playlist_uuid', 'url_music']):
            return
            
        # Diffuser à tout le groupe
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'music_start',
                'track': data.get('track'),
                'playlist_uuid': data.get('playlist_uuid'),
                'url_music': data.get('url_music'),
                'sender': self.channel_name
            }
        )

    async def handle_music_stop(self, data):
        """Gère l'arrêt de musique"""
        if await self._check_missing_params(data, ['playlist_uuid']):
            return
        
        # Diffuser à tout le groupe
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'music_stop',
                'track': data.get('track'),
                'playlist_uuid': data.get('playlist_uuid'),
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
            
    async def handle_mixer_update(self, data_received):
        data = data_received.get('data', {})
        if await self._check_missing_params(data, ['type', 'value']):
            return
        
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'mixer_update',
                'type_mixer': data.get('type'),
                'value': data.get('value')
            }
        )
        
    async def mixer_update(self, event):
        """Reçoit les messages mixer_update du groupe"""
        # Ne pas renvoyer le message à l'expéditeur
        if event.get('sender') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'mixer_update',
                'data' : {
                    'typeMixer':event.get('type_mixer', None),
                    'value':event.get('value', None),
                }
            }))
            
    async def handle_playlist_update_volume(self, data_received):
        
        data = data_received.get('data', {})
        if await self._check_missing_params(data, ['playlist_uuid', 'volume']):
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'playlist_update_volume',
                'playlist_uuid': data.get('playlist_uuid'),
                'volume': data.get('volume')
            }
        )
        
    async def playlist_update_volume(self, event):
        """Reçoit les messages playlist_update_volume du groupe"""
        # Ne pas renvoyer le message à l'expéditeur
        if event.get('sender') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'playlist_update_volume',
                'data' : {
                    'playlist_uuid':event.get('playlist_uuid', None),
                    'volume':event.get('volume', None),
                }
            }))
        
    async def validate_connection(self):
        """Valide la connexion avec UUID et token"""
        try:
            # Import du modèle uniquement quand nécessaire
            shared_soundboard = await self._get_shared_soundboard()
            
            if shared_soundboard is None:
                return False
                
            # Utilisation du niveau debug pour réduire la verbosité des logs lors des connexions réussies.
            logger.debug(f"Connexion validée pour Shared Soundboard: {self.soundboard_uuid}")
            return True
            
        except Exception as e:
            logger.error(f" Erreur validation: {e}")
            return False
        
    @database_sync_to_async
    def _get_shared_soundboard(self):
        """Récupère le SharedSoundboard de manière asynchrone"""
        try:
            cache = CacheFactory.get_default_cache()
            cache_key = f"shared_soundboard:{self.soundboard_uuid}:{self.token}"
            shared_soundboard = cache.get(cache_key)
            if shared_soundboard is not None:
                return shared_soundboard
            
            # Import local pour éviter le problème AppRegistryNotReady
            from main.architecture.persistence.models.SharedSoundboard import SharedSoundboard
            from main.architecture.persistence.models.SoundBoard import SoundBoard
            
            soundboard = SoundBoard.objects.get(uuid=self.soundboard_uuid)  #TODO repository
            if not soundboard:
                return None

            shared_soundboard = SharedSoundboard.objects.filter(  #TODO repository
                soundboard=soundboard, 
                token=self.token
            ).first()
            cache.set(cache_key, shared_soundboard, timeout=Settings.get('LIMIT_CACHE_DEFAULT'))
            
            return shared_soundboard
        except SharedSoundboard.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du soundboard: {e}")
            return None
