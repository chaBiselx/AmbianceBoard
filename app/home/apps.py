from django.apps import AppConfig


class UploadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'
    
    def ready(self):
        import home.signals  # Importer les signals
