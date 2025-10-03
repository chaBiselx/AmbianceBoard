"""
Énumération des types d'appareils/supports.

Définit les différents types d'appareils pour lesquels
les préférences utilisateur peuvent être personnalisées.
"""

from .BaseEnum import BaseEnum

class DeviceTypeEnum(BaseEnum):
    """
    Énumération des types d'appareils supportés.
    
    Définit les différents types d'appareils :
    - MOBILE : Téléphone mobile/smartphone
    - TABLET : Tablette
    - DESKTOP : Ordinateur de bureau/portable
    """
    
    MOBILE = 'mobile'
    TABLET = 'tablet'
    DESKTOP = 'desktop'