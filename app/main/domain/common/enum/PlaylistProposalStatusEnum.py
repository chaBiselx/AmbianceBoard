"""
Énumération des statuts d'une proposition de playlist sur un soundboard public.
"""

from .BaseEnum import BaseEnum


class PlaylistProposalStatusEnum(BaseEnum):
    """
    Statuts possibles d'une proposition de playlist :
    - PENDING : en attente de décision du propriétaire du soundboard
    - ACCEPTED : acceptée, la playlist a été dupliquée et ajoutée au soundboard
    - REFUSED : refusée par le propriétaire du soundboard
    """

    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REFUSED = 'refused'
