import uuid
import os
from home.utils.uuidUtils import is_not_uuid_with_extension
from django.db import models
from home.message.ReduceBiteRateMessenger import reduce_bit_rate
from .Track import Track

class Music(Track):
    MUSIC_FOLDER = 'musics/'
    fileName = models.CharField(max_length=255)
    file = models.FileField(upload_to=MUSIC_FOLDER)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._file_original = self.file if self.pk else None 
    
    def save(self, *args, **kwargs):
        new_file = False
        if self.file and  (is_not_uuid_with_extension(self.file.name) or self.__is_new_file()): #Remplacement
            self.fileName = self.file.name.split('.')[0][0:63]  
            self.__replace_name_by_uuid()
            new_file = True

        super().save(*args, **kwargs)
        if new_file: 
            reduce_bit_rate.apply_async(args=[self.file.path], queue='default', priority=1 )
            
    def get_name(self):
        if self.alternativeName:
            return self.alternativeName
        return os.path.splitext(os.path.basename(self.fileName))[0]

        
    def clean(self):
        if self.pk:
            self._file_changed = self.file != self._file_original
        super().clean()
        
    def __replace_name_by_uuid(self):
        new_uuid = uuid.uuid4()
        self.file.name = f"{new_uuid}.{self.file.name.split('.')[-1]}"
        
    def __is_new_file(self) -> bool :
        return hasattr(self, '_file_changed') and self._file_changed