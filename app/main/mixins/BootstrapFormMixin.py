"""
Mixin pour l'application automatique de styles Bootstrap aux formulaires.

Applique les classes CSS Bootstrap et les modifications de labels
de manière cohérente sur tous les formulaires de l'application.
"""

from typing import Any
from main.strategy.FormStategy import FormStategy

class BootstrapFormMixin:
    """
    Mixin pour l'application automatique de styles Bootstrap aux formulaires.
    
    Ajoute automatiquement les classes CSS Bootstrap appropriées
    à tous les champs du formulaire et gère l'affichage des labels
    avec indicateurs de champs obligatoires.
    """
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialise le mixin et applique les styles Bootstrap.
        
        Args:
            *args: Arguments positionnels pour la classe parent
            **kwargs: Arguments nommés pour la classe parent
        """
        super().__init__(*args, **kwargs)
        self._add_input_classes()
        self._add_label_classes()

    def _add_input_classes(self) -> None:
        """
        Ajoute les classes CSS appropriées aux champs de saisie.
        
        Utilise le pattern Strategy pour appliquer les classes
        selon le type de champ (input, select, checkbox, etc.).
        """
        for field in self.fields.values():
            manager = FormStategy().get_input_manager(field)
            manager.apply_classes()

    def _add_label_classes(self) -> None:
        """
        Modifie les labels des champs pour indiquer les champs obligatoires.
        
        Ajoute un astérisque (*) aux labels des champs obligatoires
        pour améliorer l'expérience utilisateur.
        """
        for field_name, field in self.fields.items():
            # Si le champ est obligatoire, ajoute un astérisque au label
            if field.required and field.label:
                field.label += ' * '
            else :
                ' '

