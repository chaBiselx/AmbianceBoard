from django.apps import AppConfig


class UploadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    # Indiquer le nouveau chemin des migrations
    migrations_module = 'main.architecture.persistence.migrations'
    
    def ready(self) -> None:
        import main.signals  # Importer les signals
