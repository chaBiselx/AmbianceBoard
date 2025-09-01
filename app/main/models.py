# Ce fichier maintient la compatibilité avec la découverte automatique des modèles Django
# Il importe tous les modèles depuis la nouvelle architecture DDD

# Import simple de tous les modèles depuis la nouvelle architecture
from .architecture.persistence.models import *
