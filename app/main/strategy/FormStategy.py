from main.strategy.formManager.InputManager import InputManager, PasswordInput, TextInputManager, FileInputManager, NumberInputManager, CheckboxInputManager, SelectInputManager

class FormStategy:
    def get_input_manager(self, field) -> InputManager:
        manager = InputManager(field)
        if(field.widget.__class__.__name__ == 'PasswordInput'):
            manager = PasswordInput(field)
        if(field.widget.__class__.__name__ == 'TextInput'):
            manager = TextInputManager(field)
        if(field.widget.__class__.__name__ == 'EmailInput'):
            manager = TextInputManager(field)
        if(field.widget.__class__.__name__ == 'Textarea'):
            manager = TextInputManager(field)
        if  field.widget.__class__.__name__ == 'FileInput':
            manager = FileInputManager(field)
        if field.widget.__class__.__name__ == 'NumberInput':
            manager = NumberInputManager(field)
        if field.widget.__class__.__name__ == 'CheckboxInput':
            manager = CheckboxInputManager(field)
        if field.widget.__class__.__name__ == 'Select':
            manager = SelectInputManager(field)
        return manager

