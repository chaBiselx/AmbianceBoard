

class BootstrapFormMixin:
    
    
    """Ajoute la classe 'form-control' à tous les champs du formulaire"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_input_classes()
        self._add_label_classes()

    def _add_input_classes(self):
        for field in self.fields.values():
            manager = InputManager(field)
            if(field.widget.__class__.__name__ == 'PasswordInput'):
                manager = PasswordInput(field)
            if(field.widget.__class__.__name__ == 'TextInput'):
                manager = TextInputManager(field)
            if  field.widget.__class__.__name__ == 'FileInput':
                manager = FileInputManager(field)
            if field.widget.__class__.__name__ == 'NumberInput':
                manager = NumberInputManager(field)
            if field.widget.__class__.__name__ == 'CheckboxInput':
                manager = CheckboxInputManager(field)
            if field.widget.__class__.__name__ == 'Select':
                manager = SelectInputManager(field)
            manager.apply_classes()

    def _add_label_classes(self):
        for field_name, field in self.fields.items():
            # Si le champ est obligatoire, ajoute un astérisque au label
            if field.required and field.label:
                field.label += ' * '
            else :
                ' '



class InputManager:
    field = None
    default_classes = ""
    added_classes = None
    
    def __init__(self, field):
        self.field = field

    def apply_classes(self):
        if(self.added_classes is not None):
            self.field.widget.attrs['class'] = f'{self._get_default_classes()} {self.added_classes}'.strip()
        
    def _get_default_classes(self):
        return self.field.widget.attrs.get('class', '')
    
class TextInputManager(InputManager): 
    default_classes = "form-control"
    
    def apply_classes(self):
        self.added_classes = self.default_classes
        if self.field.widget.attrs.get('typeInput', '') == 'color':
            self.added_classes += " form-control-color"
        super().apply_classes()
        
        
class PasswordInput(InputManager): 
    default_classes = "form-control"
    def apply_classes(self):
        self.added_classes = self.default_classes
        super().apply_classes()

class FileInputManager(InputManager): 
    default_classes = "form-control"
    
    def apply_classes(self):
        self.added_classes = self.default_classes
        super().apply_classes()
        

class NumberInputManager(InputManager): 
    default_classes = "form-control"
    
    def apply_classes(self):
        self.added_classes = self.default_classes
        if self.field.widget.attrs.get('typeInput', '') == 'range':
            self.added_classes = "form-range"
        super().apply_classes()

class CheckboxInputManager(InputManager): 
    default_classes = "form-check-input"
    
    def apply_classes(self):
        self.added_classes = self.default_classes
        super().apply_classes()
        
class SelectInputManager(InputManager): 
    default_classes = "form-select"
    
    def apply_classes(self):
        self.added_classes = self.default_classes
        super().apply_classes()
