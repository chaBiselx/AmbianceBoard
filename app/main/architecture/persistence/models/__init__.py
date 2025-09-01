import os
import importlib
import inspect
from pathlib import Path
from django.db import models

# Répertoire actuel (dossier models)
current_dir = Path(__file__).parent

# Liste pour stocker tous les modèles exportés
__all__ = []

# Parcourir tous les fichiers Python dans le répertoire models
for file_path in current_dir.glob('*.py'):
    # Ignorer __init__.py et les fichiers commençant par _
    if file_path.name.startswith('_'):
        continue
    
    # Nom du module (nom du fichier sans .py)
    module_name = file_path.stem
    
    try:
        # Importer dynamiquement le module
        module = importlib.import_module(f'.{module_name}', package=__name__)
        
        # Chercher toutes les classes dans le module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Vérifier si c'est un modèle Django (hérite de models.Model)
            if (issubclass(obj, models.Model) and 
                obj.__module__ == module.__name__ and  # Défini dans ce module
                not obj._meta.abstract):  # Pas un modèle abstrait
                
                # Ajouter au namespace global
                globals()[name] = obj
                if name not in __all__:
                    __all__.append(name)
                    
    except (ImportError, AttributeError) as e:
        # En cas d'erreur d'import, continuer avec le fichier suivant
        pass

# Trier __all__ pour une meilleure lisibilité
__all__.sort()