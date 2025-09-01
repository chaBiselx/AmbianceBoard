from django.apps import AppConfig

class UiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main.architecture.ui'
    label = 'main_ui'  # Évite les conflits de noms
