from typing import Any, Optional, List
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SharedSoundboard import SharedSoundboard
from django.utils import timezone
from datetime import timedelta


class SharedSoundboardRepository:
    
    def create(self, soundboard: SoundBoard) -> SharedSoundboard:
        return SharedSoundboard.objects.create(
            soundboard=soundboard
        )
    
    def get_or_create_for_owner(self, soundboard: SoundBoard) -> SharedSoundboard:
        """
        Récupère ou crée une session WebSocket par défaut pour le propriétaire.
        Réutilise une session existante non expirée, sinon en crée une nouvelle.
        Les sessions propriétaires ont une expiration de 30 jours.
        
        Args:
            soundboard: Le soundboard pour lequel créer/récupérer la session
            
        Returns:
            SharedSoundboard: La session WebSocket (existante ou nouvellement créée)
        """
        # Chercher une session non expirée pour ce soundboard
        existing = SharedSoundboard.objects.filter(
            soundboard=soundboard,
            expiration_date__gt=timezone.now()
        ).order_by('-expiration_date').first()
        
        if existing:
            return existing
        
        # Créer une nouvelle session avec expiration à 30 jours
        shared = SharedSoundboard.objects.create(
            soundboard=soundboard
        )
        shared.expiration_date = timezone.now() + timedelta(days=30)
        shared.save()
        return shared

    def get(self, soundboard: SoundBoard, token: str) -> SharedSoundboard|None:
        try:
            return SharedSoundboard.objects.filter(
                soundboard=soundboard,
                token=token
            ).first()
        except SharedSoundboard.DoesNotExist:
            return None

    def delete_expired(self):
        SharedSoundboard.objects.filter(expiration_date__lte=timezone.now()).delete()


