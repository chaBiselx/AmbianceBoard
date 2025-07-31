import os
import uuid

def is_not_uuid_with_extension(filename: str) -> bool:
    name, _ = os.path.splitext(os.path.basename(filename))  # Sépare le nom de l'extension
    return is_not_uuid(name)


def is_not_uuid(filename: str) -> bool:
    try:
        # Essaye de convertir le nom en UUID
        str(uuid.UUID(filename))
        return False  # Si ça fonctionne, ce n'est pas invalide
    except ValueError:
        return True  # S