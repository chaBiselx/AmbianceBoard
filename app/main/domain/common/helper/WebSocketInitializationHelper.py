"""
Helper pour initialiser automatiquement les sessions WebSocket sur les pages de soundboard.
Évite la duplication de code entre les différentes vues (privé, public, partagé).
"""
import base64
from django.urls import reverse
from django.http import HttpResponse
from main.architecture.persistence.repository.SharedSoundboardRepository import SharedSoundboardRepository
from main.domain.common.utils.url import get_full_ws
from main.architecture.persistence.repository.SoundBoardRepository import SoundBoardRepository



class WebSocketInitializationHelper:
    """
    Helper pour gérer l'initialisation automatique des sessions WebSocket.
    """
    
    @staticmethod
    def setup_websocket_board_cookies(response: HttpResponse, request, soundboard_uuid: str) -> HttpResponse:
        """
        Configure les cookies WebSocket sur une réponse HTTP pour permettre 
        l'initialisation automatique du WebSocket côté client.
        
        Args:
            response: La réponse HTTP sur laquelle ajouter les cookies
            request: La requête Django pour obtenir l'hôte
            soundboard_uuid: UUID du soundboard
            
        Returns:
            HttpResponse: La réponse avec les cookies configurés
        """
        
        soundboard = SoundBoardRepository().get(soundboard_uuid)
        if not soundboard:
            return response
        
        # Créer ou récupérer la session WebSocket
        shared = SharedSoundboardRepository().get_or_create_for_owner(soundboard=soundboard)
        
        # Générer l'URL WebSocket
        ws_path = reverse('soundboard_ws', kwargs={
            'soundboard_uuid': soundboard_uuid,
            'token': shared.token,
        })
        ws_url = get_full_ws(f'{request.get_host()}{ws_path}')
        
        # Définir les cookies WebSocket
        response.set_cookie(
            'WebSocketToken', 
            shared.token, 
            max_age=3600*24*30,  # 30 jours
            httponly=False,
            secure=True,
            samesite='Strict'
        )
        response.set_cookie(
            'WebSocketUrl', 
            base64.urlsafe_b64encode(ws_url.encode('utf-8')).decode('utf-8'),
            max_age=3600*24*30,  # 30 jours
            httponly=False,
            secure=True,
            samesite='Strict'
        )
        
        return response
