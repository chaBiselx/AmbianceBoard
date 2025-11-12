from django.apps import AppConfig


class UploadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    # Indiquer le nouveau chemin des migrations
    migrations_module = 'main.architecture.persistence.migrations'
    
    def ready(self) -> None:
        import main.architecture.messaging.events.signals  # Importer les signals
        import main.interface.admin.admin  # Importer la configuration admin
