
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
