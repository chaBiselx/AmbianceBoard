class SoundboardScriptException(Exception):
    """Exception de base pour les erreurs liées aux scripts de soundboard."""
    pass


class InvalidScriptStepException(SoundboardScriptException):
    """Exception levée quand une étape de script est invalide."""
    pass
