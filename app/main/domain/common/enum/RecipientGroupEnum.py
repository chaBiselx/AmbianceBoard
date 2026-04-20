"""
Énumération des groupes de destinataires pour l'envoi d'emails par les managers.

Définit les groupes prédéfinis permettant de cibler rapidement
un ensemble d'utilisateurs.
"""

from main.domain.common.enum.BaseEnum import BaseEnum


class RecipientGroupEnum(BaseEnum):
    """
    Énumération des groupes de destinataires pour l'envoi d'emails.

    Chaque membre définit un groupe prédéfini d'utilisateurs
    pouvant être ciblé par un manager.
    """

    ALL = "Tous les utilisateurs"
    NON_MANAGER = "Tous les utilisateurs sauf managers"
    BASIC = "Tous les utilisateurs basiques"

    @classmethod
    def get_form_choices(cls):
        """
        Retourne les choix formatés pour un champ de formulaire Django,
        avec une option vide pour la sélection manuelle.

        Returns:
            List[tuple]: Liste de tuples (value, label) pour forms.ChoiceField
        """
        choices = [('', '-- Sélection manuelle --')]
        for member in cls:
            choices.append((member.name.lower(), member.value))
        return choices
