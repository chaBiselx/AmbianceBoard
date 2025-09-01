"""
Énumération des groupes d'utilisateurs.

Définit les différents niveaux d'autorisation dans l'application.
"""

from .BaseEnum import BaseEnum

class GroupEnum(BaseEnum):
    """
    Énumération des groupes d'utilisateurs disponibles.
    
    Définit la hiérarchie des permissions :
    - ADMIN : Accès complet au système
    - MANAGER : Gestion des utilisateurs et des rôles
    - MODERATEUR : Modération du contenu
    - USER_STANDARD : Utilisateur standard
    """
    
    ADMIN = 'admin',
    MANAGER = 'manager',
    MODERATEUR = 'moderateur',
    USER_STANDARD = 'user standard',