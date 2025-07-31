"""
Utilitaires pour la validation et manipulation des UUID.

Ce module fournit des fonctions pour vérifier si une chaîne de caractères
est un UUID valide, avec ou sans extension de fichier.
"""

import os
import uuid

def is_not_uuid_with_extension(filename: str) -> bool:
    """
    Vérifie si le nom d'un fichier (sans son extension) n'est pas un UUID valide.
    
    Args:
        filename (str): Nom du fichier avec son extension
        
    Returns:
        bool: True si le nom du fichier (sans extension) n'est pas un UUID valide,
              False sinon
              
    Example:
        >>> is_not_uuid_with_extension("550e8400-e29b-41d4-a716-446655440000.jpg")
        False
        >>> is_not_uuid_with_extension("mon_fichier.jpg")
        True
    """
    name, _ = os.path.splitext(os.path.basename(filename))  # Sépare le nom de l'extension
    return is_not_uuid(name)


def is_not_uuid(filename: str) -> bool:
    """
    Vérifie si une chaîne de caractères n'est pas un UUID valide.
    
    Args:
        filename (str): Chaîne à vérifier
        
    Returns:
        bool: True si la chaîne n'est pas un UUID valide,
              False si c'est un UUID valide
              
    Example:
        >>> is_not_uuid("550e8400-e29b-41d4-a716-446655440000")
        False
        >>> is_not_uuid("not-a-uuid")
        True
    """
    try:
        # Essaye de convertir le nom en UUID
        str(uuid.UUID(filename))
        return False  # Si ça fonctionne, ce n'est pas invalide
    except ValueError:
        return True  # Si ça échoue, ce n'est pas un UUID valide