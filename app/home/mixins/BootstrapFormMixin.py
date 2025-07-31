from typing import Any
from home.strategy.FormStategy import FormStategy

class BootstrapFormMixin:
    
    
    """Ajoute la classe 'form-control' à tous les champs du formulaire"""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._add_input_classes()
        self._add_label_classes()

    def _add_input_classes(self) -> None:
        for field in self.fields.values():
            manager = FormStategy().get_input_manager(field)
            manager.apply_classes()

    def _add_label_classes(self) -> None:
        for field_name, field in self.fields.items():
            # Si le champ est obligatoire, ajoute un astérisque au label
            if field.required and field.label:
                field.label += ' * '
            else :
                ' '

