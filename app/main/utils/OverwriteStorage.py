from django.core.files.storage import FileSystemStorage
import os

class OverwriteStorage(FileSystemStorage):
    """
    Si un fichier du même nom existe, on le supprime,
    ce qui évite à Django d’ajouter un suffixe au nouveau nom.
    """
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(self.location, name))
        return name