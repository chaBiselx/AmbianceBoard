"""
Décorateur pour la détection et gestion des utilisateurs bannis.

Vérifie si le propriétaire d'un soundboard est banni et bloque
l'accès en cas de bannissement actif.
"""

from typing import Callable, Any
import functools
from django.http import HttpRequest, HttpResponse
from main.architecture.persistence.models.SoundBoard import SoundBoard
from django.shortcuts import render
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum

def detect_ban(func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    """
    Décorateur pour détecter les utilisateurs bannis.
    
    Vérifie si le propriétaire du soundboard demandé est banni.
    Si c'est le cas, retourne une page d'erreur 404 au lieu du contenu.
    
    Args:
        func: Fonction de vue à décorer
        
    Returns:
        Callable: Fonction décorée avec vérification de bannissement
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> HttpResponse:
        """
        Wrapper qui effectue la vérification de bannissement.
        
        Args:
            *args: Arguments positionnels de la vue
            **kwargs: Arguments nommés de la vue (doit contenir soundboard_uuid)
            
        Returns:
            HttpResponse: Page d'erreur 404 si banni, sinon résultat de la vue originale
        """
        if kwargs['soundboard_uuid'] is not None:
            try:
                soundboard = SoundBoard.objects.get(uuid=kwargs['soundboard_uuid'])
                if soundboard.user.checkBanned(): 
                    return render(args[0], HtmlDefaultPageEnum.ERROR_404.value, status=404)
            except SoundBoard.DoesNotExist:
                pass
        return func(*args, **kwargs)
    return wrapper