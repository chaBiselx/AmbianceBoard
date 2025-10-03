"""
Utilitaire pour la détection du type d'appareil.

Fournit des méthodes pour détecter le type d'appareil utilisé
par l'utilisateur basé sur le User-Agent de la requête HTTP.
"""

import re
from main.domain.common.enum.DeviceTypeEnum import DeviceTypeEnum


def detect_device_type(request):
    """
    Détecte le type d'appareil basé sur le User-Agent de la requête.
    
    Args:
        request: Objet request Django contenant les métadonnées HTTP
        
    Returns:
        str: Type d'appareil (DeviceTypeEnum.MOBILE, TABLET, ou DESKTOP)
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    
    # Détection mobile
    mobile_patterns = [
        r'mobile', r'android', r'iphone', r'ipod', r'blackberry', 
        r'windows phone', r'palm', r'symbian', r'opera mini'
    ]
    
    # Détection tablette
    tablet_patterns = [
        r'ipad', r'android(?!.*mobile)', r'tablet', r'kindle', 
        r'silk', r'playbook'
    ]
    
    for pattern in mobile_patterns:
        if re.search(pattern, user_agent):
            return DeviceTypeEnum.MOBILE.value
    
    for pattern in tablet_patterns:
        if re.search(pattern, user_agent):
            return DeviceTypeEnum.TABLET.value
    
    return DeviceTypeEnum.DESKTOP.value


def is_mobile(request):
    """
    Vérifie si la requête provient d'un appareil mobile.
    
    Args:
        request: Objet request Django
        
    Returns:
        bool: True si mobile, False sinon
    """
    return detect_device_type(request) == DeviceTypeEnum.MOBILE.value


def is_tablet(request):
    """
    Vérifie si la requête provient d'une tablette.
    
    Args:
        request: Objet request Django
        
    Returns:
        bool: True si tablette, False sinon
    """
    return detect_device_type(request) == DeviceTypeEnum.TABLET.value


def is_desktop(request):
    """
    Vérifie si la requête provient d'un ordinateur de bureau.
    
    Args:
        request: Objet request Django
        
    Returns:
        bool: True si desktop, False sinon
    """
    return detect_device_type(request) == DeviceTypeEnum.DESKTOP.value