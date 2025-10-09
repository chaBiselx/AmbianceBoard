from dataclasses import dataclass
from typing import Optional
from django.http import HttpRequest
import json
from main.domain.common.enum.ModerationModelEnum import ModerationModelEnum


@dataclass
class UpdateSoundPlaylistDto:
    """DTO pour les données de mise à jour d'une playlist sonore"""
    
    soundboard_uuid: Optional[str] = None
    playlist_uuid: Optional[str] = None
    soundboard_playlist_id: Optional[str] = None
    label: Optional[str] = None
    value: Optional[str] = None


    
    @classmethod
    def from_request(cls, request: HttpRequest) -> 'UpdateSoundPlaylistDto':
        """Créer un DTO à partir d'une requête HTTP"""
        # Gérer les données selon la méthode HTTP
        if request.method == 'POST':
            data = request.POST
        elif request.method in [ 'UPDATE']:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                data = {}
        else:
            data = {}
        return cls(
            soundboard_uuid=data.get('soundboard_uuid'),
            playlist_uuid=data.get('playlist_uuid'),
            soundboard_playlist_id=data.get('soundboard_playlist_id'),
            label=data.get('label'),
            value=data.get('value'),
        )
