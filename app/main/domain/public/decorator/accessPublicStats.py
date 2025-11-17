"""
Décorateur pour contrôler l'accès aux statistiques publiques.

Vérifie si l'utilisateur a le droit d'accéder aux statistiques publiques
en fonction de son tier/abonnement.
"""

from typing import Callable, Any
import functools
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.domain.common.utils.UserTierManager import UserTierManager


def can_show_statistics(func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    """
    Décorateur pour vérifier l'accès aux statistiques publiques.
    
    Vérifie si l'utilisateur a la permission 'get_statistics_from_public'.
    Si ce n'est pas le cas, retourne une page d'erreur 403.
    
    Args:
        func: Fonction de vue à décorer
        
    Returns:
        Callable: Fonction décorée avec vérification des permissions
    """
    @functools.wraps(func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Wrapper qui effectue la vérification des permissions.
        
        Args:
            request: Requête HTTP
            *args: Arguments positionnels de la vue
            **kwargs: Arguments nommés de la vue
            
        Returns:
            HttpResponse: Page d'erreur 403 si non autorisé, sinon résultat de la vue originale
        """
        has_access = UserTierManager.can_boolean(request.user, 'get_statistics_from_public')
        test = UserTierManager.get_user_limits(request.user)
        if not has_access:
            return render(request, HtmlDefaultPageEnum.ERROR_403.value, status=403)
        return func(request, *args, **kwargs)
    return wrapper