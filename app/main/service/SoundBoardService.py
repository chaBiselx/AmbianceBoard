from typing import Optional
from django.http import HttpRequest
from main.models.SoundBoard import SoundBoard
from main.models.SharedSoundboard import SharedSoundboard
from main.forms.SoundBoardForm import SoundBoardForm
from main.enum.PermissionEnum import PermissionEnum
from django.contrib import messages
from main.factory.UserParametersFactory import UserParametersFactory


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
        
    def get_all_soundboard(self) -> list[SoundBoard]:
        """
        Récupère tous les soundboards de l'utilisateur connecté.
        
        Returns:
            list[SoundBoard]: Liste des soundboards de l'utilisateur, 
                             ordonnés par date de mise à jour, 
                             liste vide en cas d'erreur
        """
        try:
            _query_set = SoundBoard.objects.all().order_by('updated_at')
            soundboards = _query_set.filter(user=self.request.user)
        except Exception:
            soundboards = []
        return soundboards
    
    def get_soundboard(self, soundboard_uuid: int) -> Optional[SoundBoard]:
        """
        Récupère un soundboard spécifique appartenant à l'utilisateur connecté.
        
        Args:
            soundboard_uuid (int): UUID du soundboard à récupérer
            
        Returns:
            Optional[SoundBoard]: Le soundboard si trouvé et appartenant à l'utilisateur,
                                 None sinon
        """
        try:
            soundboard = SoundBoard.objects.get(uuid=soundboard_uuid)
            if not soundboard or soundboard.user != self.request.user:
                return None
            return soundboard
        except SoundBoard.DoesNotExist:
            return None
    
    def get_public_soundboard(self, soundboard_uuid: int) -> Optional[SoundBoard]:
        """
        Récupère un soundboard public.
        
        Args:
            soundboard_uuid (int): UUID du soundboard à récupérer
            
        Returns:
            Optional[SoundBoard]: Le soundboard s'il est trouvé et public,
                                 None sinon
        """
        try:
            soundboard = SoundBoard.objects.get(uuid=soundboard_uuid)
            if not soundboard or not soundboard.is_public:
                return None
            return soundboard
        except SoundBoard.DoesNotExist:
            return None
        
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
        try:
            soundboard = SoundBoard.objects.get(uuid=soundboard_uuid)
            if not soundboard:
                return None
            
            shared_soundboard = SharedSoundboard.objects.get(soundboard=soundboard, token=token)
            if not shared_soundboard : 
                return None
            return soundboard

        except SoundBoard.DoesNotExist:
            return None
        except SharedSoundboard.DoesNotExist:
            return None
        
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
        
        if len(SoundBoard.objects.filter(user=self.request.user)) >= limit_soundboard:
            messages.error(self.request, "Vous avez atteint la limite de soundboard (" + str(limit_soundboard) + " max).")
            return None
        
        form = SoundBoardForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            soundboard = form.save(commit=False)
            soundboard.user = self.request.user
            soundboard.save()
            return soundboard
        return None
        

        