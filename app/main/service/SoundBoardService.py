from typing import Optional
from django.http import HttpRequest
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.interface.ui.forms.private.SoundBoardForm import SoundBoardForm
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.common.factory.UserParametersFactory import UserParametersFactory
from main.domain.common.utils.ServerNotificationBuilder import ServerNotificationBuilder
from main.architecture.persistence.repository.SoundBoardRepository import SoundBoardRepository
from main.architecture.persistence.repository.SharedSoundboardRepository import SharedSoundboardRepository


class SoundBoardService:
    """
    Service pour la gestion des soundboards.
    
    Fournit des méthodes pour récupérer, créer et gérer les soundboards
    avec gestion des permissions et des limites utilisateur.
    """
    
    def __init__(self, request: HttpRequest) -> None:
        """
        Initialise le service avec la requête HTTP.
        
        Args:
            request (HttpRequest): Requête HTTP contenant l'utilisateur connecté
        """
        self.request = request
        self.soundboard_repository = SoundBoardRepository()
        
    
    def get_soundboard(self, soundboard_uuid: int) -> Optional[SoundBoard]:
        """
        Récupère un soundboard spécifique appartenant à l'utilisateur connecté.
        
        Args:
            soundboard_uuid (int): UUID du soundboard à récupérer
            
        Returns:
            Optional[SoundBoard]: Le soundboard si trouvé et appartenant à l'utilisateur,
                                 None sinon
        """
        soundboard = self.soundboard_repository.get(soundboard_uuid)
        if not soundboard or soundboard.user != self.request.user:
            return None
        return soundboard
      
    
    def get_public_soundboard(self, soundboard_uuid: int) -> Optional[SoundBoard]:
        """
        Récupère un soundboard public.
        
        Args:
            soundboard_uuid (int): UUID du soundboard à récupérer
            
        Returns:
            Optional[SoundBoard]: Le soundboard s'il est trouvé et public,
                                 None sinon
        """
        soundboard = self.soundboard_repository.get(soundboard_uuid)
        if not soundboard or not soundboard.is_public:
            return None
        return soundboard
     
    def get_soundboard_from_shared_soundboard(self, soundboard_uuid: int, token: str) -> Optional[SoundBoard]:
        """
        Récupère un soundboard via un lien de partage avec token.
        
        Args:
            soundboard_uuid (int): UUID du soundboard à récupérer
            token (str): Token de partage pour accéder au soundboard
            
        Returns:
            Optional[SoundBoard]: Le soundboard si le token est valide,
                                 None sinon
        """
        soundboard = self.soundboard_repository.get(soundboard_uuid)
        if not soundboard:
            return None

        shared_soundboard = SharedSoundboardRepository().get(soundboard=soundboard, token=token)
        if not shared_soundboard:
            return None
        return soundboard

      
        
    def save_form(self) -> Optional[SoundBoard]:
        """
        Sauvegarde un nouveau soundboard à partir des données de formulaire.
        
        Vérifie la limite de soundboards de l'utilisateur avant création.
        Associe automatiquement l'utilisateur connecté au soundboard.
        
        Returns:
            Optional[SoundBoard]: Le soundboard créé si succès,
                                 None si échec (limite atteinte ou formulaire invalide)
        """
        user_parameters = UserParametersFactory(self.request.user)
        limit_soundboard = user_parameters.limit_soundboard

        if self.soundboard_repository.get_count_with_user(self.request.user) >= limit_soundboard:
            ServerNotificationBuilder(self.request).set_message(
                "Vous avez atteint la limite de soundboard (" + str(limit_soundboard) + " max)."
            ).set_statut("error").send()
            return None
        
        form = SoundBoardForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            soundboard = form.save(commit=False)
            soundboard.user = self.request.user
            soundboard.save()
            return soundboard
        return None
        

        