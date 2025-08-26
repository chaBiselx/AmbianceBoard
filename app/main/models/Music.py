import uuid
import os
from typing import Any
from main.utils.uuidUtils import is_not_uuid_with_extension
from django.db import models
from main.domain.brokers.message.ReduceBiteRateMessenger import reduce_bit_rate
from .Track import Track

class Music(Track):
    """
    Modèle représentant un fichier audio uploadé.
    
    Hérite de Track et gère les fichiers audio uploadés par les utilisateurs.
    Renomme automatiquement les fichiers avec des UUID pour éviter les conflits
    et lance la réduction du bitrate en arrière-plan pour optimiser l'espace disque.
    """
    
    MUSIC_FOLDER = 'musics/'
    fileName = models.CharField(max_length=255)
    file = models.FileField(upload_to=MUSIC_FOLDER)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialise une nouvelle instance de Music.
        
        Sauvegarde l'état original du fichier pour détecter les changements.
        
        Args:
            *args: Arguments positionnels pour le modèle Django
            **kwargs: Arguments nommés pour le modèle Django
        """
        super().__init__(*args, **kwargs)
        self._file_original = self.file if self.pk else None 
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Sauvegarde le fichier musical avec traitement automatique.
        
        Renomme le fichier avec un UUID si nécessaire et lance la tâche
        de réduction du bitrate en arrière-plan pour les nouveaux fichiers.
        
        Args:
            *args: Arguments positionnels pour la méthode save
            **kwargs: Arguments nommés pour la méthode save
        """
        new_file = False
        if self.file and  (is_not_uuid_with_extension(self.file.name) or self.__is_new_file()): #Remplacement
            self.fileName = self.file.name.split('.')[0][0:63]  
            self.__replace_name_by_uuid()
            new_file = True

        super().save(*args, **kwargs)
        if new_file: 
            reduce_bit_rate.apply_async(args=[self.file.path], queue='default', priority=1 )
            
    def get_name(self) -> str:
        """
        Récupère le nom d'affichage du fichier musical.
        
        Returns:
            str: Le nom alternatif s'il existe, sinon le nom du fichier sans extension
        """
        if self.alternativeName:
            return self.alternativeName
        return os.path.splitext(os.path.basename(self.fileName))[0]

    def clean(self) -> None:
        """
        Valide et nettoie les données du modèle.
        
        Détecte si le fichier a été modifié pour les instances existantes.
        """
        if self.pk:
            self._file_changed = self.file != self._file_original
        super().clean()
        
    def __replace_name_by_uuid(self) -> None:
        """
        Remplace le nom du fichier par un UUID.
        
        Génère un nouvel UUID et renomme le fichier en conservant l'extension.
        Cette méthode privée est utilisée lors de la sauvegarde pour éviter les conflits.
        """
        new_uuid = uuid.uuid4()
        self.file.name = f"{new_uuid}.{self.file.name.split('.')[-1]}"
        
    def __is_new_file(self) -> bool:
        """
        Détermine si un nouveau fichier a été uploadé.
        
        Returns:
            bool: True si le fichier a été modifié, False sinon
        """
        return hasattr(self, '_file_changed') and self._file_changed